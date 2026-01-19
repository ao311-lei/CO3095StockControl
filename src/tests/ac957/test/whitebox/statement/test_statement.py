import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService
from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService
from Service.product_service import ProductService
from Service.purchase_order_service import PurchaseOrderService


# =========================
# BudgetRepo + BudgetService
# =========================

class TestBudgetRepoAndServiceStatement(unittest.TestCase):
    def test_budget_repo_and_service_execute_lines(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "budgets.txt")
            repo = BudgetRepo(filename=path)
            svc = BudgetService(repo)

            # Repo: empty load
            repo.load_budget_record()

            # Repo: save then load
            repo.save_budget_record("2026-01", 100.0, 5.0)
            repo.load_budget_record()

            # Repo: month key
            repo.current_month_key()

            # Service: view + remaining
            svc.view_monthly_budget()
            svc.get_budget_remaining()

            # Service: set budget validations
            svc.set_monthly_budget("   ")
            svc.set_monthly_budget("abc")
            svc.set_monthly_budget("-1")
            svc.set_monthly_budget("500")

            # Service: add spend
            svc.add_spend("25")
            try:
                svc.add_spend("abc")
            except ValueError:
                pass

            # Service: month rollover branch
            repo.save_budget_record("1999-01", 123.0, 50.0)
            svc.view_monthly_budget()


# =============================
# FavouriteRepo + FavouriteService
# =============================

class TestFavouriteRepoAndServiceStatement(unittest.TestCase):
    def test_favourite_repo_and_service_execute_lines(self):
        with tempfile.TemporaryDirectory() as td:
            fav_path = os.path.join(td, "favourites.txt")
            fav_repo = FavouriteRepo(filename=fav_path)

            # Repo: empty load
            fav_repo.load_all()

            # Repo: save/load round trip
            fav_repo.save_all([("anetta", "SKU001"), ("bob", "SKU002")])
            fav_repo.load_all()

            # Repo: checks + updates
            fav_repo.is_favourite("anetta", "SKU001")
            fav_repo.add_favourite("anetta", "SKU003")
            fav_repo.get_favourites("anetta")
            fav_repo.remove_favourite("anetta", "SKU001")

            # Product lookup dependency: mock only
            product_repo = MagicMock()
            product_repo.find_by_sku.side_effect = lambda sku: {"sku": sku} if sku in ("SKU001", "SKU002") else None

            # Not logged in branches
            svc_not_logged = FavouriteService(fav_repo, product_repo, auth_service=None)
            svc_not_logged._get_username()
            svc_not_logged.favourite_product("SKU001")
            svc_not_logged.get_favourites()
            svc_not_logged.unfavourite_product("SKU001")

            # Logged in branches (auth mock)
            auth = MagicMock()
            auth.current_user = MagicMock()
            auth.current_user.username = "anetta"

            svc = FavouriteService(fav_repo, product_repo, auth_service=auth)

            svc._get_username()
            svc.favourite_product("   ")
            svc.favourite_product("SKU999")
            svc.favourite_product("SKU001")
            svc.favourite_product("SKU001")  # already favourited
            svc.get_favourites()
            svc.unfavourite_product("   ")
            svc.unfavourite_product("SKU404")
            svc.unfavourite_product("SKU001")


# =================
# ProductService
# =================

class TestProductServiceStatement(unittest.TestCase):
    def test_product_service_execute_lines(self):
        # Mock repo + category repo (no dummy classes)
        repo = MagicMock()
        cat_repo = MagicMock()

        # Make some mock "product" objects (just mocks with attributes)
        p1 = MagicMock(sku="SKU001", name="Apple", description="Fresh", category="Fruit",
                       quantity=5, price=1.5, active=True)
        p2 = MagicMock(sku="SKU002", name="Banana", description="Yellow", category="Fruit",
                       quantity=20, price=0.75, active=True)
        p3 = MagicMock(sku="SKU003", name="Detergent", description="Laundry", category="Cleaning",
                       quantity=2, price=4.0, active=True)
        inactive = MagicMock(sku="SKU999", name="Old", description="Inactive", category="Other",
                             quantity=1, price=9.99, active=False)

        all_products = [p1, p2, p3, inactive]

        repo.get_all_products.return_value = list(all_products)
        repo.find_by_sku.side_effect = lambda sku: next((p for p in all_products if p.sku == sku), None)
        repo.save_product = MagicMock()

        service = ProductService(repo, cat_repo)
        service.write_audit = lambda msg: None  # stop real audit writes

        # deactivate_product branches
        service.deactivate_product(" ")
        service.deactivate_product("NOPE")
        service.deactivate_product("SKU999")
        service.deactivate_product("SKU001", user="anetta")

        # reactivate_product branches
        service.reactivate_product(" ")
        service.reactivate_product("NOPE")
        service.reactivate_product("SKU002")
        inactive.active = False
        service.reactivate_product("SKU999")

        # search_products branches
        service.search_products(" ")
        service.search_products("sku001")
        service.search_products("banana")
        service.search_products("laundry")

        # filter_products branches
        service.filter_products()
        service.filter_products(category=" fruit ")
        service.filter_products(max_qty="5")
        service.filter_products(max_qty="abc")
        service.filter_products(sort_by="name")
        service.filter_products(sort_by="quantity")
        service.filter_products(sort_by="price")

        # view_all_products_with_status branches
        service.view_all_products_with_status()
        service.view_all_products_with_status(low_stock=1)

        # out of stock branch
        p0 = MagicMock(sku="SKU000", name="Zero", description="None", category="Other",
                       quantity=0, price=1.0, active=True)
        all_products.append(p0)
        repo.get_all_products.return_value = list(all_products)

        service.view_all_products_with_status(low_stock=5)

        # get_low_stock_products branches
        service.get_low_stock_products("abc")
        service.get_low_stock_products(-1)
        service.get_low_stock_products(5)

        # bad product branch for estimate invalid data
        bad = MagicMock(sku="BAD", name="Bad", description="Bad", category="Other",
                        quantity="x", price="y", active=True)
        all_products.append(bad)
        repo.get_all_products.return_value = list(all_products)
        repo.find_by_sku.side_effect = lambda sku: next((p for p in all_products if p.sku == sku), None)

        # estimate_restock_cost_for_sku branches
        service.estimate_restock_cost_for_sku(" ", 10)
        service.estimate_restock_cost_for_sku("SKU001", "x")
        service.estimate_restock_cost_for_sku("SKU001", -1)
        service.estimate_restock_cost_for_sku("NOPE", 10)
        service.estimate_restock_cost_for_sku("SKU999", 10)
        service.estimate_restock_cost_for_sku("BAD", 10)
        service.estimate_restock_cost_for_sku("SKU002", 10)
        service.estimate_restock_cost_for_sku("SKU001", 10)

        # estimate_restock_cost_for_multiple_skus branch
        service.estimate_restock_cost_for_multiple_skus([
            ("SKU001", 10),
            ("NOPE", 10),
            ("SKU999", 10),
            ("SKU002", 10),
        ])


# ======================
# PurchaseOrderService
# ======================

class DummyPurchaseOrder:
    def __init__(self, po_id, expected_date, user, status):
        self.po_id = po_id
        self.expected_date = expected_date
        self.user = user
        self.status = status


class DummyPurchaseOrderLine:
    def __init__(self, po_id, sku, quantity):
        self.po_id = po_id
        self.sku = sku
        self.quantity = quantity


class TestPurchaseOrderServiceStatement(unittest.TestCase):
    def test_purchase_order_service_execute_lines(self):
        svc = PurchaseOrderService.__new__(PurchaseOrderService)

        # Mock repos (no dummy repos)
        svc.product_repo = MagicMock()
        svc.repo = MagicMock()

        # Products returned by product_repo.find_by_sku
        prod_active = MagicMock(sku="SKU1", price=5.0, active=True)
        prod_inactive = MagicMock(sku="SKU9", price=99.0, active=False)

        svc.product_repo.find_by_sku.side_effect = lambda sku: {"SKU1": prod_active, "SKU9": prod_inactive}.get(sku)

        # Validators + audit sink
        svc.validate_date = lambda d: True
        svc.validate_quantity = lambda q: True
        svc.write_audit = lambda msg: None

        # budget_service mock (uses .budget_repo inside)
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = (None, None, None)
        budget_service = MagicMock()
        budget_service.budget_repo = budget_repo

        # _get_monthly_budget_amount branches
        svc._get_monthly_budget_amount(None)
        svc._get_monthly_budget_amount(budget_service)

        # _print_budget_after_purchase branches
        with patch("builtins.print"):
            svc._print_budget_after_purchase(None)
            svc._print_budget_after_purchase(budget_service)

        # _add_to_budget_spent branch when missing
        svc._add_to_budget_spent(None, 10)

        # create_purchase_order branches (invalid date, empty lines, invalid qty)
        with patch("builtins.print"):
            svc.validate_date = lambda d: False
            svc.create_purchase_order("bad-date", [{"sku": "SKU1", "quantity": 1}], "anetta")

            svc.validate_date = lambda d: True
            svc.create_purchase_order("2026-01-10", [], "anetta")

            svc.validate_quantity = lambda q: False
            svc.create_purchase_order("2026-01-10", [{"sku": "SKU1", "quantity": 1}], "anetta")

        # budget paths: blocked + allowed
        svc.validate_quantity = lambda q: True

        # Blocked (budget too low)
        over_budget_repo = MagicMock()
        over_budget_repo.current_month_key.return_value = "2026-01"
        over_budget_repo.load_budget_record.return_value = ("2026-01", 5.0, 0.0)
        over_budget_service = MagicMock(budget_repo=over_budget_repo)

        # Allowed
        ok_budget_repo = MagicMock()
        ok_budget_repo.current_month_key.return_value = "2026-01"
        ok_budget_repo.load_budget_record.return_value = ("2026-01", 50.0, 5.0)
        ok_budget_service = MagicMock(budget_repo=ok_budget_repo)

        with patch("builtins.print"), \
             patch("Service.purchase_order_service.PurchaseOrder", DummyPurchaseOrder), \
             patch("Service.purchase_order_service.PurchaseOrderLine", DummyPurchaseOrderLine), \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260103060000"

            svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=over_budget_service
            )

        with patch("builtins.print"), \
             patch("Service.purchase_order_service.PurchaseOrder", DummyPurchaseOrder), \
             patch("Service.purchase_order_service.PurchaseOrderLine", DummyPurchaseOrderLine), \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260103060000"

            svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=ok_budget_service
            )


if __name__ == "__main__":
    unittest.main()
