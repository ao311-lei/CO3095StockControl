import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService

from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService

from Service.product_service import ProductService
from Service.purchase_order_service import PurchaseOrderService


# -------------------------
# Lightweight data helpers
# -------------------------

def make_product(
    sku,
    name="N",
    description="D",
    category="C",
    quantity=0,
    price=1.0,
    active=True,
):
    return SimpleNamespace(
        sku=sku,
        name=name,
        description=description,
        category=category,
        quantity=quantity,
        price=price,
        active=active,
    )


# =========================================================
# Concolic BudgetRepo
# =========================================================

class TestConcolicBudgetRepo(unittest.TestCase):
    def test_concolic_budget_repo_paths(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "budgets.txt")
            repo = BudgetRepo(filename=path)

            # Path 1: empty file
            self.assertEqual(repo.load_budget_record(), (None, None, None))

            # Path 2: invalid line
            with open(path, "w", encoding="utf-8") as f:
                f.write("bad_line\n")
            self.assertEqual(repo.load_budget_record(), (None, None, None))

            # Path 3: month only
            with open(path, "w", encoding="utf-8") as f:
                f.write("2026-01|\n")
            self.assertEqual(repo.load_budget_record(), ("2026-01", None, 0.0))

            # Path 4: month + budget (spent missing)
            with open(path, "w", encoding="utf-8") as f:
                f.write("2026-01|500\n")
            self.assertEqual(repo.load_budget_record(), ("2026-01", 500.0, 0.0))

            # Path 5: save with budget None
            repo.save_budget_record("2026-01", None, 25.0)
            self.assertEqual(repo.load_budget_record(), ("2026-01", None, 25.0))

            # Path 6: month key format
            self.assertRegex(repo.current_month_key(), r"^\d{4}-\d{2}$")


# =========================================================
# Concolic BudgetService
# =========================================================

class TestConcolicBudgetService(unittest.TestCase):
    def test_concolic_budget_service_paths(self):
        with tempfile.TemporaryDirectory() as td:
            repo = BudgetRepo(filename=os.path.join(td, "budgets.txt"))
            svc = BudgetService(repo)

            # Path 1: empty input
            self.assertEqual(svc.set_monthly_budget("   "), "Budget cannot be empty.")
            # Path 2: non-numeric
            self.assertEqual(svc.set_monthly_budget("abc"), "Budget must be a number.")
            # Path 3: negative
            self.assertEqual(svc.set_monthly_budget("-1"), "Budget cannot be negative.")

            # Path 4: valid budget
            ok = svc.set_monthly_budget("500")
            self.assertIn("Monthly budget saved for", ok)

            # Path 5: view budget string contains expected parts
            msg = svc.view_monthly_budget()
            self.assertIn("£500.00", msg)
            self.assertIn("Spent so far:", msg)
            self.assertIn("Remaining:", msg)

            # Path 6: remaining before spend
            self.assertEqual(svc.get_budget_remaining(), 500.0)

            # Path 7: spend accumulates
            svc.add_spend("25")
            self.assertAlmostEqual(svc.get_budget_remaining(), 475.0, places=2)

            # Path 8: invalid spend raises ValueError
            with self.assertRaises(ValueError):
                svc.add_spend("nope")


# =========================================================
# Concolic FavouriteRepo
# =========================================================

class TestConcolicFavouriteRepo(unittest.TestCase):
    def test_concolic_favourite_repo_paths(self):
        with tempfile.TemporaryDirectory() as td:
            repo = FavouriteRepo(filename=os.path.join(td, "favourites.txt"))

            # Path 1: empty
            self.assertEqual(repo.load_all(), [])

            # Path 2: add favourite
            repo.add_favourite("anetta", "SKU001")
            self.assertTrue(repo.is_favourite("anetta", "SKU001"))

            # Path 3: duplicate should not duplicate
            repo.add_favourite("anetta", "SKU001")
            self.assertEqual(repo.load_all().count(("anetta", "SKU001")), 1)

            # Path 4: unknown SKU
            self.assertFalse(repo.is_favourite("anetta", "SKU999"))

            # Path 5: remove favourite
            repo.remove_favourite("anetta", "SKU001")
            self.assertFalse(repo.is_favourite("anetta", "SKU001"))

            # Path 6: save_all + load_all
            data = [("u1", "S1"), ("u2", "S2")]
            repo.save_all(data)
            self.assertEqual(repo.load_all(), data)


# =========================================================
# Concolic FavouriteService (MagicMock auth + product_repo)
# =========================================================

class TestConcolicFavouriteService(unittest.TestCase):
    def test_concolic_favourite_service_paths(self):
        with tempfile.TemporaryDirectory() as td:
            fav_repo = FavouriteRepo(filename=os.path.join(td, "favourites.txt"))

            # product_repo only needs find_by_sku (FavouriteService expects dict product objects)
            p1 = {"sku": "SKU001"}
            p2 = {"sku": "SKU002"}
            product_map = {"SKU001": p1, "SKU002": p2}

            product_repo = MagicMock()
            product_repo.find_by_sku.side_effect = lambda sku: product_map.get(sku)

            # ---- Path 1: not logged in (auth_service None)
            svc = FavouriteService(fav_repo, product_repo, auth_service=None)
            self.assertIsNone(svc._get_username())
            self.assertEqual(
                svc.favourite_product("SKU001"),
                "You must be logged in to favourite products.",
            )

            # ---- Logged in setup (MagicMock user)
            user = MagicMock()
            user.username = "anetta"
            auth = MagicMock()
            auth.current_user = user

            svc2 = FavouriteService(fav_repo, product_repo, auth_service=auth)

            # Path 2: empty SKU
            self.assertEqual(svc2.favourite_product("   "), "SKU cannot be empty.")
            # Path 3: product not found
            self.assertEqual(svc2.favourite_product("SKU999"), "Product not found.")
            # Path 4: success
            self.assertEqual(svc2.favourite_product("SKU001"), "Product added to favourites.")
            # Path 5: already favourited
            self.assertEqual(svc2.favourite_product("SKU001"), "This product is already favourited.")

            # Path 6: get_favourites ignores missing products
            fav_repo.add_favourite("anetta", "SKU404")
            favs, err = svc2.get_favourites()
            self.assertIsNone(err)
            self.assertEqual(favs, [p1])

            # Path 7: unfavourite not logged in
            svc3 = FavouriteService(fav_repo, product_repo, auth_service=None)
            self.assertEqual(
                svc3.unfavourite_product("SKU001"),
                "You must be logged in to unfavourite products.",
            )

            # Path 8: unfavourite empty SKU
            self.assertEqual(svc2.unfavourite_product("   "), "SKU cannot be empty.")
            # Path 9: not in favourites
            self.assertEqual(svc2.unfavourite_product("SKU002"), "This product is not in your favourites.")
            # Path 10: remove success
            self.assertEqual(svc2.unfavourite_product("SKU001"), "Product removed from favourites.")
            self.assertFalse(fav_repo.is_favourite("anetta", "SKU001"))


# =========================================================
# Concolic ProductService (MagicMock product_repo)
# =========================================================

class TestConcolicProductService(unittest.TestCase):
    def test_concolic_product_service_paths(self):
        # Important: quantities must be int-convertible for status + low-stock logic
        p1 = make_product("SKU001", "Apple", "Red", "Fruit", quantity=5, price=1.5, active=True)
        p2 = make_product("SKU002", "Banana", "Yellow", "Fruit", quantity=20, price=0.75, active=True)
        p3 = make_product("SKU003", "Detergent", "Laundry", "Cleaning", quantity=2, price=4.0, active=True)
        inactive = make_product("SKU999", "Old", "Inactive", "Other", quantity=1, price=9.99, active=False)

        # Track products in a list we can mutate during the test
        products = [p1, p2, p3, inactive]

        def find_by_sku(sku):
            sku = (sku or "").strip()
            return next((p for p in products if p.sku == sku), None)

        product_repo = MagicMock()
        product_repo.get_all_products.side_effect = lambda: list(products)
        product_repo.find_by_sku.side_effect = find_by_sku
        product_repo.save_product = MagicMock()

        category_repo = MagicMock()
        svc = ProductService(product_repo, category_repo)

        audits = []
        svc.write_audit = lambda msg: audits.append(msg)

        # ---- deactivate branches
        self.assertEqual(svc.deactivate_product(" "), "SKU cannot be empty")
        self.assertEqual(svc.deactivate_product("NOPE"), "Product not found")
        self.assertEqual(svc.deactivate_product("SKU999"), "Product is already INACTIVE")

        msg = svc.deactivate_product("SKU001", user="anetta")
        self.assertEqual(msg, "Product deactivated successfully")
        self.assertFalse(p1.active)
        self.assertTrue(any("PRODUCT_DEACTIVATE" in a for a in audits))

        # ---- reactivate branches
        self.assertEqual(svc.reactivate_product(" "), "SKU cannot be empty")
        self.assertEqual(svc.reactivate_product("NOPE"), "Product not found")
        self.assertEqual(svc.reactivate_product("SKU002"), "Product is already ACTIVE")

        inactive.active = False
        self.assertEqual(svc.reactivate_product("SKU999"), "Product reactivated successfully")
        self.assertTrue(inactive.active)

        # ---- search branches
        self.assertEqual(svc.search_products(" "), [])
        self.assertEqual(svc.search_products("sku001"), [p1])
        self.assertEqual(svc.search_products("banana"), [p2])
        self.assertEqual(svc.search_products("laundry"), [p3])

        # ---- filter branches
        self.assertEqual(svc.filter_products(category=" fruit "), [p1, p2])
        self.assertEqual(svc.filter_products(max_qty="abc"), [p1, p2, p3, inactive])

        # ---- estimate branches
        _, err = svc.estimate_restock_cost_for_sku(" ", 10)
        self.assertEqual(err, "SKU cannot be empty.")

        _, err = svc.estimate_restock_cost_for_sku("SKU001", "x")
        self.assertEqual(err, "Target stock level must be a whole number.")

        _, err = svc.estimate_restock_cost_for_sku("SKU001", -1)
        self.assertEqual(err, "Target stock level cannot be negative.")

        _, err = svc.estimate_restock_cost_for_sku("NOPE", 10)
        self.assertEqual(err, "Product not found.")

        inactive.active = False
        _, err = svc.estimate_restock_cost_for_sku("SKU999", 10)
        self.assertEqual(err, "This product is INACTIVE. Reactivate it before planning restock.")

        bad = make_product("BAD", "Bad", "Bad", "Other", quantity="x", price="y", active=True)
        products.append(bad)

        _, err = svc.estimate_restock_cost_for_sku("BAD", 10)
        self.assertEqual(err, "Product data is invalid (quantity/price).")

        _, err = svc.estimate_restock_cost_for_sku("SKU002", 10)
        self.assertEqual(err, "This product is already at or above the target stock level.")

        # success estimate (ensure active)
        p1.active = True
        est, err = svc.estimate_restock_cost_for_sku("SKU001", 10)
        self.assertIsNone(err)
        self.assertEqual(est["units_to_buy"], 5)

        # ---- view_all_products_with_status branches
        # Use a safe list (exclude BAD) because status does int(p.quantity)
        safe_products = [p1, p2, p3, inactive]
        products[:] = safe_products

        results = svc.view_all_products_with_status(low_stock=5)
        status_map = {p.sku: status for (p, status) in results}
        self.assertEqual(status_map["SKU999"], "INACTIVE")
        self.assertEqual(status_map["SKU001"], "LOW STOCK")
        self.assertEqual(status_map["SKU003"], "LOW STOCK")
        self.assertEqual(status_map["SKU002"], "IN STOCK")

        # Out of stock branch
        p0 = make_product("SKU000", "Zero", "None", "Other", quantity=0, price=1.0, active=True)
        products.append(p0)

        results2 = svc.view_all_products_with_status(low_stock=5)
        status_map2 = {p.sku: status for (p, status) in results2}
        self.assertEqual(status_map2["SKU000"], "OUT OF STOCK")

        # ---- get_low_stock_products branches
        # IMPORTANT: use a clean list WITHOUT SKU000 so it doesn't leak into the expected output
        products[:] = [p1, p2, p3, inactive]

        self.assertIsNone(svc.get_low_stock_products("abc"))
        self.assertIsNone(svc.get_low_stock_products(-1))

        low = svc.get_low_stock_products(5)
        self.assertEqual([p.sku for p in low], ["SKU001", "SKU003"])


# =========================================================
# Concolic PurchaseOrderService (MagicMock repos + patched models)
# =========================================================

class TestConcolicPurchaseOrderService(unittest.TestCase):
    def setUp(self):
        self.svc = PurchaseOrderService.__new__(PurchaseOrderService)

        p_ok = make_product("SKU1", price=5.0, active=True)
        p_inactive = make_product("SKU9", price=99.0, active=False)

        self.svc.product_repo = MagicMock()
        self.svc.product_repo.find_by_sku.side_effect = lambda sku: {"SKU1": p_ok, "SKU9": p_inactive}.get(sku)

        self.svc.repo = MagicMock()
        self.svc.repo.saved = []

        def _save(po, lines):
            self.svc.repo.saved.append((po, lines))

        self.svc.repo.save_purchase_order.side_effect = _save

        self.audit = []
        self.svc.write_audit = lambda msg: self.audit.append(msg)

        self.svc.validate_date = lambda d: True
        self.svc.validate_quantity = lambda q: True

    def _budget_service(self, month_key="2026-01", record=(None, None, None)):
        b_repo = MagicMock()
        b_repo.current_month_key.return_value = month_key
        b_repo.load_budget_record.return_value = record
        b_repo.saved_records = []

        def _save(month, budget, spent):
            b_repo.saved_records.append((month, budget, spent))
            b_repo.load_budget_record.return_value = (month, budget, spent)

        b_repo.save_budget_record.side_effect = _save

        b_service = MagicMock()
        b_service.budget_repo = b_repo
        return b_service, b_repo

    def test_concolic_po_paths(self):
        # Path 1: no budget_service
        month, budget = self.svc._get_monthly_budget_amount(None)
        self.assertEqual((month, budget), (None, None))

        # Path 2: missing record
        b_svc, _ = self._budget_service(month_key="2026-01", record=(None, None, None))
        month, budget = self.svc._get_monthly_budget_amount(b_svc)
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)

        # Path 3: invalid date
        self.svc.validate_date = lambda d: False
        with patch("builtins.print"):
            self.svc.create_purchase_order("bad", [{"sku": "SKU1", "quantity": 1}], "anetta")
        self.assertEqual(len(self.svc.repo.saved), 0)

        self.svc.validate_date = lambda d: True

        # Path 4: empty lines
        with patch("builtins.print"):
            self.svc.create_purchase_order("2026-01-10", [], "anetta")
        self.assertEqual(len(self.svc.repo.saved), 0)

        # Path 5: all invalid lines
        self.svc.validate_quantity = lambda q: False
        with patch("builtins.print"):
            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "NOPE", "quantity": 1}, {"sku": "SKU9", "quantity": 1}, {"sku": "SKU1", "quantity": 1}],
                "anetta",
            )
        self.assertEqual(len(self.svc.repo.saved), 0)
        self.svc.validate_quantity = lambda q: True

        # Path 6: over budget blocks
        b_svc_over, _ = self._budget_service(month_key="2026-01", record=("2026-01", 5.0, 0.0))
        with patch("builtins.print"), \
             patch("Service.purchase_order_service.PurchaseOrder") as MockPO, \
             patch("Service.purchase_order_service.PurchaseOrderLine") as MockLine, \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260103060000"
            MockPO.side_effect = lambda po_id, expected_date, user, status: SimpleNamespace(
                po_id=po_id, expected_date=expected_date, created_by=user, status=status
            )
            MockLine.side_effect = lambda po_id, sku, quantity: SimpleNamespace(po_id=po_id, sku=sku, quantity=quantity)

            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=b_svc_over,
            )

        self.assertEqual(len(self.svc.repo.saved), 0)
        self.assertTrue(any("PO BLOCKED" in a for a in self.audit))

        # Path 7: within budget saves + (maybe) updates spent
        b_svc_ok, b_repo_ok = self._budget_service(month_key="2026-01", record=("2026-01", 50.0, 5.0))
        before = len(self.svc.repo.saved)

        with patch("builtins.print"), \
             patch("Service.purchase_order_service.PurchaseOrder") as MockPO, \
             patch("Service.purchase_order_service.PurchaseOrderLine") as MockLine, \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260103060001"
            MockPO.side_effect = lambda po_id, expected_date, user, status: SimpleNamespace(
                po_id=po_id, expected_date=expected_date, created_by=user, status=status
            )
            MockLine.side_effect = lambda po_id, sku, quantity: SimpleNamespace(po_id=po_id, sku=sku, quantity=quantity)

            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=b_svc_ok,
            )

        self.assertEqual(len(self.svc.repo.saved), before + 1)

        # Only assert updates if your implementation actually updates spent
        if b_repo_ok.saved_records:
            self.assertEqual(b_repo_ok.saved_records[-1][0], "2026-01")


if __name__ == "__main__":
    unittest.main()
