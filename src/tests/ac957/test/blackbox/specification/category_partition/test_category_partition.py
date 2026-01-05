import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Import the real services/repos we are testing
from Service.purchase_order_service import PurchaseOrderService
from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService
from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService
from Service.product_service import ProductService


# =========================
# BudgetRepo tests
# =========================

class TestBudgetRepoCategoryPartition(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpfile = os.path.join(self.tmpdir.name, "budgets.txt")
        self.repo = BudgetRepo(filename=self.tmpfile)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_init_creates_file_if_missing(self):
        self.assertTrue(os.path.exists(self.tmpfile))

    def test_load_empty_file_returns_none_tuple(self):
        self.assertEqual(self.repo.load_budget_record(), (None, None, None))

    def test_load_invalid_format_returns_none_tuple(self):
        with open(self.tmpfile, "w", encoding="utf-8") as f:
            f.write("invalid_line\n")
        self.assertEqual(self.repo.load_budget_record(), (None, None, None))

    def test_load_month_only_budget_empty_defaults(self):
        with open(self.tmpfile, "w", encoding="utf-8") as f:
            f.write("2026-01|\n")
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)
        self.assertEqual(spent, 0.0)

    def test_load_month_and_budget_no_spent_defaults_to_zero(self):
        with open(self.tmpfile, "w", encoding="utf-8") as f:
            f.write("2026-01|50000\n")
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertEqual(budget, 50000.0)
        self.assertEqual(spent, 0.0)

    def test_load_full_record(self):
        self.repo.save_budget_record("2026-01", 50000.0, 190.0)
        self.assertEqual(self.repo.load_budget_record(), ("2026-01", 50000.0, 190.0))

    def test_load_empty_spent_defaults_to_zero(self):
        with open(self.tmpfile, "w", encoding="utf-8") as f:
            f.write("2026-01|50000|\n")
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertEqual(budget, 50000.0)
        self.assertEqual(spent, 0.0)

    def test_save_budget_none_writes_empty_budget_field(self):
        self.repo.save_budget_record("2026-01", None, 25.0)
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)
        self.assertEqual(spent, 25.0)

    def test_current_month_key_format(self):
        key = self.repo.current_month_key()
        self.assertRegex(key, r"^\d{4}-\d{2}$")


# =========================
# BudgetService tests
# =========================

class TestBudgetServiceCategoryPartition(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpfile = os.path.join(self.tmpdir.name, "budgets.txt")

        self.repo = BudgetRepo(filename=self.tmpfile)
        self.service = BudgetService(self.repo)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_set_budget_empty_rejected(self):
        self.assertEqual(self.service.set_monthly_budget("   "), "Budget cannot be empty.")

    def test_set_budget_non_numeric_rejected(self):
        self.assertEqual(self.service.set_monthly_budget("abc"), "Budget must be a number.")

    def test_set_budget_negative_rejected(self):
        self.assertEqual(self.service.set_monthly_budget("-1"), "Budget cannot be negative.")

    def test_set_budget_zero_accepted(self):
        msg = self.service.set_monthly_budget("0")
        self.assertIn("Monthly budget saved for", msg)
        _, budget, spent = self.repo.load_budget_record()
        self.assertEqual(budget, 0.0)
        self.assertEqual(spent, 0.0)

    def test_set_budget_trimmed_numeric_accepted(self):
        msg = self.service.set_monthly_budget(" 500 ")
        self.assertIn("£500.00", msg)

    def test_set_budget_preserves_existing_spent(self):
        month_key = self.repo.current_month_key()
        self.repo.save_budget_record(month_key, 100.0, 190.0)

        self.service.set_monthly_budget("500")
        _, budget, spent = self.repo.load_budget_record()
        self.assertEqual(budget, 500.0)
        self.assertEqual(spent, 190.0)

    def test_view_budget_when_none_set(self):
        msg = self.service.view_monthly_budget()
        self.assertIn("No budget set for", msg)
        self.assertIsNone(self.service.get_budget_remaining())

    def test_view_budget_with_spent_and_remaining(self):
        month_key = self.repo.current_month_key()
        self.repo.save_budget_record(month_key, 500.0, 190.0)

        msg = self.service.view_monthly_budget()
        self.assertIn("£500.00", msg)
        self.assertIn("Spent so far: £190.00", msg)
        self.assertIn("Remaining: £310.00", msg)
        self.assertEqual(self.service.get_budget_remaining(), 310.0)

    def test_add_spend_no_budget_returns_message(self):
        result = self.service.add_spend("25")
        self.assertEqual(result, "No budget set.")

    def test_add_spend_adds_amount(self):
        self.service.set_monthly_budget("500")
        self.service.add_spend("25")
        _, budget, spent = self.repo.load_budget_record()
        self.assertEqual(budget, 500.0)
        self.assertEqual(spent, 25.0)

    def test_add_spend_accumulates(self):
        self.service.set_monthly_budget("500")
        self.service.add_spend("25")
        self.service.add_spend("40")
        _, _, spent = self.repo.load_budget_record()
        self.assertEqual(spent, 65.0)

    def test_add_spend_non_numeric_raises_value_error(self):
        self.service.set_monthly_budget("500")
        with self.assertRaises(ValueError):
            self.service.add_spend("abc")


# =========================
# FavouriteRepo tests
# =========================

class TestFavouriteRepo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpfile = os.path.join(self.tmpdir.name, "favourites.txt")
        self.repo = FavouriteRepo(filename=self.tmpfile)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_init_creates_file_if_missing(self):
        self.assertTrue(os.path.exists(self.tmpfile))

    def test_load_all_empty_file_returns_empty_list(self):
        self.assertEqual(self.repo.load_all(), [])

    def test_save_all_then_load_all_round_trip(self):
        data = [("anetta", "SKU001"), ("bob", "SKU002")]
        self.repo.save_all(data)
        self.assertEqual(self.repo.load_all(), data)

    def test_load_all_strips_spaces(self):
        with open(self.tmpfile, "w", encoding="utf-8") as f:
            f.write("  anetta  ,  SKU001  \n")
            f.write("\n")
            f.write("bob,SKU002\n")
        self.assertEqual(self.repo.load_all(), [("anetta", "SKU001"), ("bob", "SKU002")])

    def test_is_favourite_true_and_false(self):
        self.repo.save_all([("anetta", "SKU001")])
        self.assertTrue(self.repo.is_favourite("anetta", "SKU001"))
        self.assertFalse(self.repo.is_favourite("anetta", "SKU999"))

    def test_add_favourite_adds_when_missing(self):
        self.repo.add_favourite("anetta", "SKU001")
        self.assertTrue(self.repo.is_favourite("anetta", "SKU001"))

    def test_add_favourite_does_not_duplicate(self):
        self.repo.add_favourite("anetta", "SKU001")
        self.repo.add_favourite("anetta", "SKU001")
        self.assertEqual(self.repo.load_all().count(("anetta", "SKU001")), 1)

    def test_get_favourites_returns_only_for_user(self):
        self.repo.save_all([("anetta", "SKU001"), ("bob", "SKU002"), ("anetta", "SKU003")])
        self.assertEqual(self.repo.get_favourites("anetta"), ["SKU001", "SKU003"])
        self.assertEqual(self.repo.get_favourites("bob"), ["SKU002"])
        self.assertEqual(self.repo.get_favourites("nobody"), [])

    def test_remove_favourite_removes_only_target(self):
        self.repo.save_all([("anetta", "SKU001"), ("anetta", "SKU002"), ("bob", "SKU001")])
        self.repo.remove_favourite("anetta", "SKU001")

        self.assertFalse(self.repo.is_favourite("anetta", "SKU001"))
        self.assertTrue(self.repo.is_favourite("anetta", "SKU002"))
        self.assertTrue(self.repo.is_favourite("bob", "SKU001"))


# =========================
# FavouriteService tests
# =========================

class TestFavouriteService(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpfile = os.path.join(self.tmpdir.name, "favourites.txt")
        self.fav_repo = FavouriteRepo(filename=self.tmpfile)

        # Replace product repo dummy with MagicMock
        self.product_repo = MagicMock()
        self.product_repo.find_by_sku.side_effect = lambda sku: (
            {"sku": "SKU001", "name": "Product 1"} if sku == "SKU001"
            else {"sku": "SKU002", "name": "Product 2"} if sku == "SKU002"
            else None
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_get_username_auth_service_none(self):
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=None)
        self.assertIsNone(service._get_username())

    def test_get_username_current_user_none(self):
        auth = MagicMock()
        auth.current_user = None
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertIsNone(service._get_username())

    def test_get_username_success(self):
        auth = MagicMock()
        auth.current_user = MagicMock(username="anetta")
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service._get_username(), "anetta")

    def test_favourite_product_requires_login(self):
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=None)
        self.assertEqual(service.favourite_product("SKU001"), "You must be logged in to favourite products.")

    def test_favourite_product_empty_sku(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service.favourite_product("   "), "SKU cannot be empty.")

    def test_favourite_product_not_found(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service.favourite_product("SKU999"), "Product not found.")

    def test_favourite_product_already_favourited(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service.favourite_product("SKU001"), "Product added to favourites.")
        self.assertEqual(service.favourite_product("SKU001"), "This product is already favourited.")

    def test_favourite_product_success_trims_sku(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        msg = service.favourite_product("  SKU001  ")
        self.assertEqual(msg, "Product added to favourites.")
        self.assertTrue(self.fav_repo.is_favourite("anetta", "SKU001"))

    def test_get_favourites_requires_login(self):
        auth = MagicMock(current_user=None)
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        products, err = service.get_favourites()
        self.assertIsNone(products)
        self.assertEqual(err, "You must be logged in to view favourites.")

    def test_get_favourites_returns_products(self):
        self.fav_repo.save_all([("anetta", "SKU001"), ("anetta", "SKU002")])
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)

        products, err = service.get_favourites()
        self.assertIsNone(err)
        self.assertEqual(products, [{"sku": "SKU001", "name": "Product 1"}, {"sku": "SKU002", "name": "Product 2"}])

    def test_get_favourites_ignores_missing_products(self):
        self.fav_repo.save_all([("anetta", "SKU001"), ("anetta", "SKU404")])
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)

        products, err = service.get_favourites()
        self.assertIsNone(err)
        self.assertEqual(products, [{"sku": "SKU001", "name": "Product 1"}])

    def test_unfavourite_product_requires_login(self):
        auth = MagicMock(current_user=None)
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service.unfavourite_product("SKU001"), "You must be logged in to unfavourite products.")

    def test_unfavourite_product_empty_sku(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service.unfavourite_product("   "), "SKU cannot be empty.")

    def test_unfavourite_product_not_in_favourites(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(service.unfavourite_product("SKU001"), "This product is not in your favourites.")

    def test_unfavourite_product_success(self):
        auth = MagicMock(current_user=MagicMock(username="anetta"))
        service = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)

        service.favourite_product("SKU001")
        self.assertTrue(self.fav_repo.is_favourite("anetta", "SKU001"))

        msg = service.unfavourite_product("SKU001")
        self.assertEqual(msg, "Product removed from favourites.")
        self.assertFalse(self.fav_repo.is_favourite("anetta", "SKU001"))


# =========================
# ProductService tests (no dummy products/repos)
# =========================

class TestProductServiceCategoryPartition(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.category_repo = MagicMock()

        # "products" are MagicMocks with the needed attributes
        self.p1 = MagicMock(sku="SKU001", name="Apple", description="Fresh red apple",
                            category="Fruit", quantity=5, price=1.5, active=True)
        self.p2 = MagicMock(sku="SKU002", name="Banana", description="Yellow banana",
                            category="Fruit", quantity=20, price=0.75, active=True)
        self.p3 = MagicMock(sku="SKU003", name="Detergent", description="Laundry soap",
                            category="Cleaning", quantity=2, price=4.0, active=True)
        self.inactive = MagicMock(sku="SKU999", name="Old Item", description="Inactive product",
                                  category="Other", quantity=1, price=9.99, active=False)

        self.products = [self.p1, self.p2, self.p3, self.inactive]

        self.repo.get_all_products.return_value = list(self.products)
        self.repo.find_by_sku.side_effect = lambda sku: next((p for p in self.products if p.sku == sku), None)
        self.repo.save_product = MagicMock()

        self.service = ProductService(self.repo, self.category_repo)

        self.audit_log = []
        self.service.write_audit = lambda msg: self.audit_log.append(msg)

    def test_deactivate_product_empty_sku(self):
        self.assertEqual(self.service.deactivate_product(" "), "SKU cannot be empty")

    def test_deactivate_product_not_found(self):
        self.assertEqual(self.service.deactivate_product("NOPE"), "Product not found")

    def test_deactivate_product_already_inactive(self):
        self.assertEqual(self.service.deactivate_product("SKU999"), "Product is already INACTIVE")

    def test_deactivate_product_success(self):
        msg = self.service.deactivate_product("SKU001", user="anetta")
        self.assertEqual(msg, "Product deactivated successfully")
        self.assertFalse(self.p1.active)
        self.repo.save_product.assert_called()
        self.assertTrue(any("PRODUCT_DEACTIVATE" in m for m in self.audit_log))

    def test_reactivate_product_empty_sku(self):
        self.assertEqual(self.service.reactivate_product(" "), "SKU cannot be empty")

    def test_reactivate_product_not_found(self):
        self.assertEqual(self.service.reactivate_product("NOPE"), "Product not found")

    def test_reactivate_product_already_active(self):
        self.assertEqual(self.service.reactivate_product("SKU001"), "Product is already ACTIVE")

    def test_reactivate_product_success(self):
        self.inactive.active = False
        msg = self.service.reactivate_product("SKU999")
        self.assertEqual(msg, "Product reactivated successfully")
        self.assertTrue(self.inactive.active)
        self.repo.save_product.assert_called()

    def test_search_products_empty_query(self):
        self.assertEqual(self.service.search_products(" "), [])

    def test_search_products_by_sku(self):
        self.assertEqual(self.service.search_products("sku001"), [self.p1])

    def test_search_products_by_name(self):
        self.assertEqual(self.service.search_products("banana"), [self.p2])

    def test_search_products_by_description(self):
        self.assertEqual(self.service.search_products("laundry"), [self.p3])

    def test_filter_products_no_filters(self):
        self.assertEqual(self.service.filter_products(), self.products)

    def test_filter_products_by_category(self):
        self.assertEqual(self.service.filter_products(category=" fruit "), [self.p1, self.p2])

    def test_filter_products_by_max_qty_valid(self):
        self.assertEqual(self.service.filter_products(max_qty="5"), [self.p1, self.p3, self.inactive])

    def test_filter_products_by_max_qty_invalid(self):
        self.assertEqual(self.service.filter_products(max_qty="abc"), self.products)

    def test_filter_products_sort_by_name(self):
        self.assertEqual(self.service.filter_products(sort_by="name"), [self.p1, self.p2, self.p3, self.inactive])

    def test_filter_products_sort_by_quantity(self):
        self.assertEqual(self.service.filter_products(sort_by="quantity"), [self.inactive, self.p3, self.p1, self.p2])

    def test_filter_products_sort_by_price(self):
        self.assertEqual(self.service.filter_products(sort_by="price"), [self.p2, self.p1, self.p3, self.inactive])

    def test_estimate_restock_cost_invalid_sku(self):
        est, err = self.service.estimate_restock_cost_for_sku(" ", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "SKU cannot be empty.")

    def test_estimate_restock_cost_invalid_target(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU001", "x")
        self.assertIsNone(est)
        self.assertEqual(err, "Target stock level must be a whole number.")

    def test_estimate_restock_cost_negative_target(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU001", -1)
        self.assertIsNone(est)
        self.assertEqual(err, "Target stock level cannot be negative.")

    def test_estimate_restock_cost_product_not_found(self):
        est, err = self.service.estimate_restock_cost_for_sku("NOPE", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "Product not found.")

    def test_estimate_restock_cost_inactive_product(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU999", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "This product is INACTIVE. Reactivate it before planning restock.")

    def test_estimate_restock_cost_invalid_product_data(self):
        bad = MagicMock(sku="BAD", name="Bad", description="Bad", category="Other",
                        quantity="x", price="y", active=True)
        self.products.append(bad)
        self.repo.get_all_products.return_value = list(self.products)

        est, err = self.service.estimate_restock_cost_for_sku("BAD", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "Product data is invalid (quantity/price).")

    def test_estimate_restock_cost_success(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU001", 10)
        self.assertIsNone(err)
        self.assertEqual(est["units_to_buy"], 5)
        self.assertEqual(est["estimated_cost"], 7.5)

    def test_estimate_restock_cost_for_multiple_skus(self):
        sku_targets = [
            ("SKU001", 10),
            ("NOPE", 10),
            ("SKU999", 10),
            ("SKU002", 10),
        ]
        breakdown, total, errors = self.service.estimate_restock_cost_for_multiple_skus(sku_targets)
        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0]["sku"], "SKU001")
        self.assertEqual(total, 7.5)
        self.assertEqual(len(errors), 3)

    def test_view_all_products_with_status_default_threshold(self):
        results = self.service.view_all_products_with_status()
        status_map = {p.sku: status for (p, status) in results}

        self.assertEqual(status_map["SKU999"], "INACTIVE")
        self.assertEqual(status_map["SKU001"], "LOW STOCK")
        self.assertEqual(status_map["SKU003"], "LOW STOCK")
        self.assertEqual(status_map["SKU002"], "IN STOCK")

    def test_view_all_products_with_status_out_of_stock(self):
        p0 = MagicMock(sku="SKU000", name="Zero", description="None left",
                       category="Other", quantity=0, price=1.0, active=True)
        self.products.append(p0)
        self.repo.get_all_products.return_value = list(self.products)

        results = self.service.view_all_products_with_status(low_stock=5)
        status_map = {p.sku: status for (p, status) in results}
        self.assertEqual(status_map["SKU000"], "OUT OF STOCK")

    def test_view_all_products_with_status_custom_threshold(self):
        results = self.service.view_all_products_with_status(low_stock=1)
        status_map = {p.sku: status for (p, status) in results}

        self.assertEqual(status_map["SKU001"], "IN STOCK")
        self.assertEqual(status_map["SKU003"], "IN STOCK")
        self.assertEqual(status_map["SKU999"], "INACTIVE")

    def test_get_low_stock_products_invalid_threshold_returns_none(self):
        self.assertIsNone(self.service.get_low_stock_products("abc"))

    def test_get_low_stock_products_negative_threshold_returns_none(self):
        self.assertIsNone(self.service.get_low_stock_products(-1))

    def test_get_low_stock_products_returns_only_active_and_qty_le_threshold(self):
        low = self.service.get_low_stock_products(5)
        self.assertEqual(low, [self.p1, self.p3])

    def test_get_low_stock_products_ignores_inactive_products(self):
        low = self.service.get_low_stock_products(100)
        self.assertNotIn(self.inactive, low)

    def test_get_low_stock_products_skips_broken_quantity_data(self):
        bad_qty = MagicMock(sku="BADQ", name="BadQty", description="Bad qty",
                            category="Other", quantity="X", price=1.0, active=True)
        self.products.append(bad_qty)
        self.repo.get_all_products.return_value = list(self.products)

        low = self.service.get_low_stock_products(10)
        self.assertNotIn(bad_qty, low)


# =========================
# PurchaseOrderService tests (no dummy repos/products)
# =========================

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


class TestPurchaseOrderServiceCategoryPartition(unittest.TestCase):
    def setUp(self):
        self.service = PurchaseOrderService.__new__(PurchaseOrderService)

        # product_repo + repo as MagicMocks
        self.service.product_repo = MagicMock()
        self.service.repo = MagicMock()

        # products returned by find_by_sku
        self.p1 = MagicMock(sku="SKU1", price=5.0, active=True)
        self.p2 = MagicMock(sku="SKU2", price=2.0, active=True)
        self.inactive = MagicMock(sku="SKU9", price=99.0, active=False)

        self.service.product_repo.find_by_sku.side_effect = lambda sku: {
            "SKU1": self.p1,
            "SKU2": self.p2,
            "SKU9": self.inactive
        }.get(sku)

        self.service.validate_date = lambda d: True
        self.service.validate_quantity = lambda q: True

        self.audit = []
        self.service.write_audit = lambda msg: self.audit.append(msg)

    def test_get_monthly_budget_amount_budget_service_none(self):
        month, budget = self.service._get_monthly_budget_amount(None)
        self.assertEqual((month, budget), (None, None))

    def test_get_monthly_budget_amount_no_record(self):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = (None, None, None)
        budget_service = MagicMock(budget_repo=budget_repo)

        month, budget = self.service._get_monthly_budget_amount(budget_service)
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)

    def test_get_monthly_budget_amount_month_mismatch(self):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-02"
        budget_repo.load_budget_record.return_value = ("2026-01", 100.0, 0.0)
        budget_service = MagicMock(budget_repo=budget_repo)

        month, budget = self.service._get_monthly_budget_amount(budget_service)
        self.assertEqual(month, "2026-02")
        self.assertIsNone(budget)

    def test_get_monthly_budget_amount_success(self):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = ("2026-01", "250.5", 10.0)
        budget_service = MagicMock(budget_repo=budget_repo)

        month, budget = self.service._get_monthly_budget_amount(budget_service)
        self.assertEqual(month, "2026-01")
        self.assertEqual(budget, 250.5)

    @patch("builtins.print")
    def test_print_budget_after_purchase_budget_service_none(self, mock_print):
        self.service._print_budget_after_purchase(None)
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_print_budget_after_purchase_no_record(self, mock_print):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = (None, None, None)
        budget_service = MagicMock(budget_repo=budget_repo)

        self.service._print_budget_after_purchase(budget_service)
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_print_budget_after_purchase_spent_none_defaults_to_zero(self, mock_print):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = ("2026-01", 100.0, None)
        budget_service = MagicMock(budget_repo=budget_repo)

        self.service._print_budget_after_purchase(budget_service)
        self.assertTrue(any("Remaining budget for 2026-01: £100.00" in c.args[0]
                            for c in mock_print.call_args_list))

    def test_add_to_budget_spent_budget_service_none(self):
        self.service._add_to_budget_spent(None, 10)

    def test_add_to_budget_spent_month_mismatch_does_nothing(self):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-02"
        budget_repo.load_budget_record.return_value = ("2026-01", 100.0, 20.0)
        budget_service = MagicMock(budget_repo=budget_repo)

        self.service._add_to_budget_spent(budget_service, 10)
        budget_repo.save_budget_record.assert_not_called()

    def test_add_to_budget_spent_spent_none_defaults_to_zero(self):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = ("2026-01", 100.0, None)
        budget_service = MagicMock(budget_repo=budget_repo)

        self.service._add_to_budget_spent(budget_service, 10)
        budget_repo.save_budget_record.assert_called_once_with("2026-01", 100.0, 10.0)

    def test_add_to_budget_spent_adds_amount(self):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = ("2026-01", 100.0, 20.0)
        budget_service = MagicMock(budget_repo=budget_repo)

        self.service._add_to_budget_spent(budget_service, 15)
        budget_repo.save_budget_record.assert_called_once_with("2026-01", 100.0, 35.0)

    @patch("builtins.print")
    def test_create_po_invalid_date(self, mock_print):
        self.service.validate_date = lambda d: False

        self.service.create_purchase_order("bad-date", [{"sku": "SKU1", "quantity": 1}], "anetta")
        self.assertTrue(any("Invalid expected delivery date" in c.args[0] for c in mock_print.call_args_list))
        self.service.repo.save_purchase_order.assert_not_called()

    @patch("builtins.print")
    def test_create_po_empty_lines(self, mock_print):
        self.service.create_purchase_order("2026-01-10", [], "anetta")
        self.assertTrue(any("Purchase order must have at least one product" in c.args[0] for c in mock_print.call_args_list))
        self.service.repo.save_purchase_order.assert_not_called()

    @patch("builtins.print")
    def test_create_po_all_lines_invalid_results_in_no_po(self, mock_print):
        self.service.validate_quantity = lambda q: False

        lines = [
            {"sku": "NOPE", "quantity": 1},
            {"sku": "SKU9", "quantity": 1},
            {"sku": "SKU1", "quantity": 1},
        ]

        self.service.create_purchase_order("2026-01-10", lines, "anetta")
        self.assertTrue(any("Purchase order must have at least one valid product" in c.args[0] for c in mock_print.call_args_list))
        self.service.repo.save_purchase_order.assert_not_called()

    @patch("builtins.print")
    def test_create_po_over_budget_blocks_and_audits(self, mock_print):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = ("2026-01", 5.0, 0.0)
        budget_service = MagicMock(budget_repo=budget_repo)

        with patch("Service.purchase_order_service.PurchaseOrder", DummyPurchaseOrder), \
             patch("Service.purchase_order_service.PurchaseOrderLine", DummyPurchaseOrderLine), \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260103060000"

            self.service.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=budget_service
            )

        self.service.repo.save_purchase_order.assert_not_called()
        self.assertTrue(any("Purchase order blocked" in c.args[0] for c in mock_print.call_args_list))
        self.assertTrue(any("PO BLOCKED" in msg for msg in self.audit))

    @patch("builtins.print")
    def test_create_po_with_budget_allows_saves_updates_spent_and_prints_remaining(self, mock_print):
        budget_repo = MagicMock()
        budget_repo.current_month_key.return_value = "2026-01"
        budget_repo.load_budget_record.return_value = ("2026-01", 50.0, 5.0)
        budget_service = MagicMock(budget_repo=budget_repo)

        with patch("Service.purchase_order_service.PurchaseOrder", DummyPurchaseOrder), \
             patch("Service.purchase_order_service.PurchaseOrderLine", DummyPurchaseOrderLine), \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260103060000"

            self.service.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=budget_service
            )

        self.service.repo.save_purchase_order.assert_called_once()

        budget_repo.save_budget_record.assert_called()
        args = budget_repo.save_budget_record.call_args[0]
        self.assertEqual(args[0], "2026-01")
        self.assertEqual(args[1], 50.0)
        self.assertEqual(args[2], 15.0)

        printed = "\n".join([c.args[0] for c in mock_print.call_args_list if c.args])
        self.assertIn("Remaining budget for 2026-01: £45.00", printed)

        self.assertTrue(any("created by anetta" in msg for msg in self.audit))


if __name__ == "__main__":
    unittest.main()
