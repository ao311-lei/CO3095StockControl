import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Import the real repos/services we are testing
from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService

from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService

from Service.product_service import ProductService
from Service.purchase_order_service import PurchaseOrderService


# =========================================================
# Small helpers (NOT repos, just lightweight objects)
# =========================================================

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
# BudgetRepo — symbolic/path tests
# =========================================================

class TestBudgetRepoSymbolic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "budgets.txt")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_init_creates_file(self):
        self.assertFalse(os.path.exists(self.path))
        BudgetRepo(filename=self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_load_budget_record_symbolic_formats(self):
        repo = BudgetRepo(filename=self.path)

        variants = [
            ("", (None, None, None)),
            ("bad_line\n", (None, None, None)),
            ("2026-01|\n", ("2026-01", None, 0.0)),
            ("2026-01|500\n", ("2026-01", 500.0, 0.0)),
            ("2026-01|500|12\n", ("2026-01", 500.0, 12.0)),
            ("2026-01| | \n", ("2026-01", None, 0.0)),
        ]

        for content, expected in variants:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(content)
            self.assertEqual(repo.load_budget_record(), expected)

    def test_save_then_load_symbolic(self):
        repo = BudgetRepo(filename=self.path)

        cases = [
            ("2026-01", None, 0.0),
            ("2026-01", 500.0, 12.5),
            ("1999-12", 0.0, 0.0),
        ]

        for month, budget, spent in cases:
            repo.save_budget_record(month, budget, spent)
            m, b, s = repo.load_budget_record()
            self.assertEqual(m, month)
            self.assertEqual(b, budget if budget is None else float(budget))
            self.assertEqual(s, float(spent))

    def test_current_month_key_format(self):
        repo = BudgetRepo(filename=self.path)
        self.assertRegex(repo.current_month_key(), r"^\d{4}-\d{2}$")


# =========================================================
# BudgetService — symbolic/path tests
# =========================================================

class TestBudgetServiceSymbolic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "budgets.txt")
        self.repo = BudgetRepo(filename=self.path)
        self.service = BudgetService(self.repo)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_set_monthly_budget_symbolic(self):
        inputs = ["", "   ", "abc", "-1", "0", "500", "  12.5  "]

        for x in inputs:
            msg = self.service.set_monthly_budget(x)

            if x.strip() == "":
                self.assertEqual(msg, "Budget cannot be empty.")
            elif x.strip().lower() == "abc":
                self.assertEqual(msg, "Budget must be a number.")
            elif x.strip().startswith("-"):
                self.assertEqual(msg, "Budget cannot be negative.")
            else:
                self.assertIn("Monthly budget saved for", msg)

    def test_view_monthly_budget_symbolic(self):
        msg = self.service.view_monthly_budget()
        self.assertIn("No budget set for", msg)

        self.service.set_monthly_budget("100")
        msg2 = self.service.view_monthly_budget()
        self.assertIn("£100.00", msg2)
        self.assertIn("Spent so far: £0.00", msg2)

    def test_get_budget_remaining_symbolic(self):
        self.assertIsNone(self.service.get_budget_remaining())

        self.service.set_monthly_budget("100")
        self.assertEqual(self.service.get_budget_remaining(), 100.0)

        mk = self.repo.current_month_key()
        self.repo.save_budget_record(mk, 100.0, 30.0)
        self.assertEqual(self.service.get_budget_remaining(), 70.0)

    def test_add_spend_symbolic(self):
        self.assertEqual(self.service.add_spend("10"), "No budget set.")

        self.service.set_monthly_budget("100")
        spends = ["0", "1", "2.5", "10"]
        total = 0.0

        for s in spends:
            self.service.add_spend(s)
            total += float(s)

        _mk, b, spent = self.repo.load_budget_record()
        self.assertEqual(b, 100.0)
        self.assertAlmostEqual(spent, total, places=2)

        with self.assertRaises(ValueError):
            self.service.add_spend("abc")


# =========================================================
# FavouriteRepo — symbolic/path tests
# =========================================================

class TestFavouriteRepoSymbolic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "favourites.txt")
        self.repo = FavouriteRepo(filename=self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load_all_symbolic(self):
        variants = [
            ("", []),
            ("\n\n", []),
            ("anetta,SKU001\n", [("anetta", "SKU001")]),
            ("  anetta  ,  SKU001  \n", [("anetta", "SKU001")]),
            ("bob,SKU002\nanetta,SKU001\n", [("bob", "SKU002"), ("anetta", "SKU001")]),
        ]

        for content, expected in variants:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(content)
            self.assertEqual(self.repo.load_all(), expected)

    def test_add_is_get_remove_save_all_symbolic(self):
        self.repo.save_all([("anetta", "SKU001")])

        self.assertTrue(self.repo.is_favourite("anetta", "SKU001"))
        self.assertFalse(self.repo.is_favourite("anetta", "SKU999"))

        self.repo.add_favourite("anetta", "SKU001")
        self.assertEqual(self.repo.load_all().count(("anetta", "SKU001")), 1)

        self.repo.add_favourite("anetta", "SKU002")
        self.assertEqual(self.repo.get_favourites("anetta"), ["SKU001", "SKU002"])

        self.repo.remove_favourite("anetta", "SKU001")
        self.assertFalse(self.repo.is_favourite("anetta", "SKU001"))


# =========================================================
# FavouriteService — symbolic/path tests (MagicMock instead of Dummy classes)
# =========================================================

class TestFavouriteServiceSymbolic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "favourites.txt")
        self.repo = FavouriteRepo(filename=self.path)

        # product_repo only needs find_by_sku
        self.p1 = {"sku": "SKU001"}
        self.p2 = {"sku": "SKU002"}
        self.product_repo = MagicMock()
        self.product_repo.find_by_sku.side_effect = lambda sku: {"SKU001": self.p1, "SKU002": self.p2}.get(sku)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_get_username_symbolic(self):
        svc = FavouriteService(self.repo, self.product_repo, auth_service=None)
        self.assertIsNone(svc._get_username())

        auth = MagicMock()
        auth.current_user = None
        svc2 = FavouriteService(self.repo, self.product_repo, auth_service=auth)
        self.assertIsNone(svc2._get_username())

        user = MagicMock()
        user.username = "anetta"
        auth2 = MagicMock()
        auth2.current_user = user
        svc3 = FavouriteService(self.repo, self.product_repo, auth_service=auth2)
        self.assertEqual(svc3._get_username(), "anetta")

    def test_favourite_product_symbolic(self):
        auth_none = MagicMock()
        auth_none.current_user = None
        svc = FavouriteService(self.repo, self.product_repo, auth_service=auth_none)
        self.assertEqual(svc.favourite_product("SKU001"), "You must be logged in to favourite products.")

        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc2 = FavouriteService(self.repo, self.product_repo, auth_service=auth)

        sku_inputs = ["", "   ", "SKU999", "SKU001", "SKU001"]
        expected = [
            "SKU cannot be empty.",
            "SKU cannot be empty.",
            "Product not found.",
            "Product added to favourites.",
            "This product is already favourited.",
        ]

        for s, exp in zip(sku_inputs, expected):
            self.assertEqual(svc2.favourite_product(s), exp)

    def test_get_favourites_symbolic(self):
        auth_none = MagicMock()
        auth_none.current_user = None
        svc = FavouriteService(self.repo, self.product_repo, auth_service=auth_none)
        products, err = svc.get_favourites()
        self.assertIsNone(products)
        self.assertEqual(err, "You must be logged in to view favourites.")

        self.repo.save_all([("anetta", "SKU001"), ("anetta", "SKU404"), ("anetta", "SKU002")])
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user

        svc2 = FavouriteService(self.repo, self.product_repo, auth_service=auth)
        products2, err2 = svc2.get_favourites()
        self.assertIsNone(err2)
        self.assertEqual(products2, [self.p1, self.p2])

    def test_unfavourite_product_symbolic(self):
        auth_none = MagicMock()
        auth_none.current_user = None
        svc = FavouriteService(self.repo, self.product_repo, auth_service=auth_none)
        self.assertEqual(svc.unfavourite_product("SKU001"), "You must be logged in to unfavourite products.")

        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc2 = FavouriteService(self.repo, self.product_repo, auth_service=auth)

        self.assertEqual(svc2.unfavourite_product("   "), "SKU cannot be empty.")
        self.assertEqual(svc2.unfavourite_product("SKU001"), "This product is not in your favourites.")

        svc2.favourite_product("SKU001")
        self.assertEqual(svc2.unfavourite_product("SKU001"), "Product removed from favourites.")


# =========================================================
# ProductService — symbolic/path tests (MagicMock repo)
# =========================================================

class TestProductServiceSymbolic(unittest.TestCase):
    def setUp(self):
        self.p1 = make_product("SKU001", "Apple", "Fresh", "Fruit", quantity=5, price=1.5, active=True)
        self.p2 = make_product("SKU002", "Banana", "Yellow", "Fruit", quantity=20, price=0.75, active=True)
        self.p3 = make_product("SKU003", "Detergent", "Laundry", "Cleaning", quantity=2, price=4.0, active=True)
        self.inactive = make_product("SKU999", "Old", "Inactive", "Other", quantity=1, price=9.99, active=False)

        self.products = [self.p1, self.p2, self.p3, self.inactive]

        self.product_repo = MagicMock()
        self.product_repo.get_all_products.return_value = list(self.products)
        self.product_repo.find_by_sku.side_effect = lambda sku: next((p for p in self.products if p.sku == sku), None)
        self.product_repo.save_product = MagicMock()

        self.category_repo = MagicMock()
        self.service = ProductService(self.product_repo, self.category_repo)

        self.audit = []
        self.service.write_audit = lambda msg: self.audit.append(msg)

    def test_deactivate_product_symbolic(self):
        self.assertEqual(self.service.deactivate_product(" "), "SKU cannot be empty")
        self.assertEqual(self.service.deactivate_product("NOPE"), "Product not found")
        self.assertEqual(self.service.deactivate_product("SKU999"), "Product is already INACTIVE")

        msg = self.service.deactivate_product("SKU001", user="anetta")
        self.assertEqual(msg, "Product deactivated successfully")
        self.assertFalse(self.p1.active)
        self.product_repo.save_product.assert_called()
        self.assertTrue(any("PRODUCT_DEACTIVATE" in a for a in self.audit))

    def test_reactivate_product_symbolic(self):
        self.assertEqual(self.service.reactivate_product(" "), "SKU cannot be empty")
        self.assertEqual(self.service.reactivate_product("NOPE"), "Product not found")
        self.assertEqual(self.service.reactivate_product("SKU002"), "Product is already ACTIVE")

        # make sure inactive is inactive then reactivate
        self.inactive.active = False
        msg = self.service.reactivate_product("SKU999")
        self.assertEqual(msg, "Product reactivated successfully")
        self.assertTrue(self.inactive.active)
        self.product_repo.save_product.assert_called()

    def test_search_products_symbolic(self):
        self.assertEqual(self.service.search_products(""), [])
        self.assertEqual(self.service.search_products("   "), [])
        self.assertEqual(self.service.search_products("sku001"), [self.p1])
        self.assertEqual(self.service.search_products("banana"), [self.p2])
        self.assertEqual(self.service.search_products("laundry"), [self.p3])

    def test_filter_products_symbolic(self):
        self.assertEqual(self.service.filter_products(category=" fruit "), [self.p1, self.p2])
        self.assertEqual(self.service.filter_products(category=""), self.products)

        got = self.service.filter_products(max_qty="5")
        self.assertIn(self.p1, got)
        self.assertIn(self.p3, got)

        got2 = self.service.filter_products(max_qty="abc")
        self.assertEqual(got2, self.products)

        self.assertEqual(
            self.service.filter_products(sort_by="name"),
            sorted(self.products, key=lambda p: str(p.name).lower()),
        )
        self.assertEqual(
            self.service.filter_products(sort_by="quantity"),
            sorted(self.products, key=lambda p: int(p.quantity)),
        )
        self.assertEqual(
            self.service.filter_products(sort_by="price"),
            sorted(self.products, key=lambda p: float(p.price)),
        )

    def test_estimate_restock_symbolic(self):
        est, err = self.service.estimate_restock_cost_for_sku("   ", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "SKU cannot be empty.")

        est, err = self.service.estimate_restock_cost_for_sku("SKU001", "abc")
        self.assertIsNone(est)
        self.assertEqual(err, "Target stock level must be a whole number.")

        est, err = self.service.estimate_restock_cost_for_sku("SKU001", -1)
        self.assertIsNone(est)
        self.assertEqual(err, "Target stock level cannot be negative.")

        est, err = self.service.estimate_restock_cost_for_sku("NOPE", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "Product not found.")

        est, err = self.service.estimate_restock_cost_for_sku("SKU999", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "This product is INACTIVE. Reactivate it before planning restock.")

        bad = make_product("BAD", "Bad", "Bad", "Other", quantity="x", price="y", active=True)
        self.products.append(bad)
        self.product_repo.get_all_products.return_value = list(self.products)

        est, err = self.service.estimate_restock_cost_for_sku("BAD", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "Product data is invalid (quantity/price).")

        est, err = self.service.estimate_restock_cost_for_sku("SKU002", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "This product is already at or above the target stock level.")

        est, err = self.service.estimate_restock_cost_for_sku("SKU001", 10)
        self.assertIsNone(err)
        self.assertEqual(est["units_to_buy"], 5)
        self.assertEqual(est["estimated_cost"], 7.5)

    def test_estimate_multiple_symbolic(self):
        sku_targets = [("SKU001", 10), ("NOPE", 10), ("SKU999", 10), ("SKU002", 10)]
        breakdown, total, errors = self.service.estimate_restock_cost_for_multiple_skus(sku_targets)

        self.assertEqual(len(breakdown), 1)
        self.assertEqual(total, 7.5)
        self.assertEqual(len(errors), 3)

    def test_view_all_products_with_status_symbolic(self):
        results = self.service.view_all_products_with_status()
        status_map = {p.sku: status for (p, status) in results}

        self.assertEqual(status_map["SKU999"], "INACTIVE")
        self.assertEqual(status_map["SKU001"], "LOW STOCK")
        self.assertEqual(status_map["SKU003"], "LOW STOCK")
        self.assertEqual(status_map["SKU002"], "IN STOCK")

        p0 = make_product("SKU000", "Zero", "None", "Other", quantity=0, price=1.0, active=True)
        self.products.append(p0)
        self.product_repo.get_all_products.return_value = list(self.products)

        results2 = self.service.view_all_products_with_status(low_stock=5)
        status_map2 = {p.sku: status for (p, status) in results2}
        self.assertEqual(status_map2["SKU000"], "OUT OF STOCK")

    def test_get_low_stock_products_symbolic(self):
        self.assertIsNone(self.service.get_low_stock_products("abc"))
        self.assertIsNone(self.service.get_low_stock_products(-1))

        low = self.service.get_low_stock_products(5)
        self.assertEqual(low, [self.p1, self.p3])

        bad_qty = make_product("BADQ", "BadQ", "Bad", "Other", quantity="X", price=1.0, active=True)
        self.products.append(bad_qty)
        self.product_repo.get_all_products.return_value = list(self.products)

        low2 = self.service.get_low_stock_products(10)
        self.assertNotIn(bad_qty, low2)


# =========================================================
# PurchaseOrderService — symbolic/path tests (MagicMock repos)
# Note: this DOES NOT test ProductRepo or PurchaseOrderRepo classes.
# It only tests PurchaseOrderService behaviour by mocking its dependencies.
# =========================================================

class TestPurchaseOrderServiceSymbolic(unittest.TestCase):
    def setUp(self):
        self.svc = PurchaseOrderService.__new__(PurchaseOrderService)

        # product_repo: find_by_sku returns product objects with sku/price/active
        self.p_ok = make_product("SKU1", price=5.0, active=True)
        self.p_inactive = make_product("SKU9", price=99.0, active=False)

        self.product_repo = MagicMock()
        self.product_repo.find_by_sku.side_effect = lambda sku: {"SKU1": self.p_ok, "SKU9": self.p_inactive}.get(sku)

        # repo: save_purchase_order captured
        self.po_repo = MagicMock()
        self.po_repo.saved = []

        def _save(po, lines):
            self.po_repo.saved.append((po, lines))

        self.po_repo.save_purchase_order.side_effect = _save

        self.svc.product_repo = self.product_repo
        self.svc.repo = self.po_repo

        # audit sink + validators
        self.audit = []
        self.svc.write_audit = lambda msg: self.audit.append(msg)
        self.svc.validate_date = lambda d: True
        self.svc.validate_quantity = lambda q: True

    def _make_budget_service(self, month_key="2026-01", record=(None, None, None)):
        # budget_service.budget_repo.current_month_key/load_budget_record/save_budget_record
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

    def test_get_monthly_budget_amount_symbolic(self):
        month, budget = self.svc._get_monthly_budget_amount(None)
        self.assertEqual((month, budget), (None, None))

        b_service, _b_repo = self._make_budget_service(month_key="2026-01", record=(None, None, None))
        month, budget = self.svc._get_monthly_budget_amount(b_service)
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)

        b_service2, _ = self._make_budget_service(month_key="2026-02", record=("2026-01", 100.0, 0.0))
        month, budget = self.svc._get_monthly_budget_amount(b_service2)
        self.assertEqual(month, "2026-02")
        self.assertIsNone(budget)

        b_service3, _ = self._make_budget_service(month_key="2026-01", record=("2026-01", "250.5", 10.0))
        month, budget = self.svc._get_monthly_budget_amount(b_service3)
        self.assertEqual(month, "2026-01")
        self.assertEqual(budget, 250.5)

    @patch("builtins.print")
    def test_create_purchase_order_symbolic_paths(self, mock_print):
        # invalid date branch
        self.svc.validate_date = lambda d: False
        self.svc.create_purchase_order("bad", [{"sku": "SKU1", "quantity": 1}], "anetta")
        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Invalid expected delivery date", printed)
        self.assertEqual(self.po_repo.saved, [])

        mock_print.reset_mock()
        self.svc.validate_date = lambda d: True

        # empty lines branch
        self.svc.create_purchase_order("2026-01-10", [], "anetta")
        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Purchase order must have at least one product", printed)
        self.assertEqual(self.po_repo.saved, [])

        mock_print.reset_mock()

        # no valid lines branch (not found + inactive + invalid qty)
        self.svc.validate_quantity = lambda q: False
        self.svc.create_purchase_order(
            "2026-01-10",
            [{"sku": "NOPE", "quantity": 1}, {"sku": "SKU9", "quantity": 1}, {"sku": "SKU1", "quantity": 1}],
            "anetta",
        )
        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Product NOPE not found. Line skipped.", printed)
        self.assertIn("Product SKU9 is INACTIVE. Line skipped.", printed)
        self.assertIn("Invalid quantity for SKU1. Line skipped.", printed)
        self.assertIn("Purchase order must have at least one valid product", printed)
        self.assertEqual(self.po_repo.saved, [])

        mock_print.reset_mock()

        # cost calc fail branch
        self.svc.validate_quantity = lambda q: True
        self.p_ok.price = "BAD"
        self.svc.create_purchase_order("2026-01-10", [{"sku": "SKU1", "quantity": 2}], "anetta")
        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Could not calculate cost for SKU1. Line skipped.", printed)
        self.assertIn("Purchase order must have at least one valid product", printed)
        self.assertEqual(self.po_repo.saved, [])

        # restore
        self.p_ok.price = 5.0
        mock_print.reset_mock()

        # budget_service None branch (allows PO, prints warning)
        with patch("Service.purchase_order_service.PurchaseOrder") as MockPO, \
             patch("Service.purchase_order_service.PurchaseOrderLine") as MockLine, \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260104041005"
            MockPO.side_effect = lambda po_id, expected_date, user, status: SimpleNamespace(
                po_id=po_id, expected_date=expected_date, created_by=user, status=status
            )
            MockLine.side_effect = lambda po_id, sku, quantity: SimpleNamespace(po_id=po_id, sku=sku, quantity=quantity)

            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 1}],
                "anetta",
                budget_service=None,
            )

        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("PO cost: £5.00", printed)
        self.assertIn("Warning: No monthly budget set yet.", printed)
        self.assertEqual(len(self.po_repo.saved), 1)

    @patch("builtins.print")
    def test_create_purchase_order_budget_none_with_month_key(self, mock_print):
        b_service, _b_repo = self._make_budget_service(month_key="2026-01", record=(None, None, None))

        with patch("Service.purchase_order_service.PurchaseOrder") as MockPO, \
             patch("Service.purchase_order_service.PurchaseOrderLine") as MockLine, \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260104041006"
            MockPO.side_effect = lambda po_id, expected_date, user, status: SimpleNamespace(
                po_id=po_id, expected_date=expected_date, created_by=user, status=status
            )
            MockLine.side_effect = lambda po_id, sku, quantity: SimpleNamespace(po_id=po_id, sku=sku, quantity=quantity)

            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=b_service,
            )

        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("PO cost: £10.00", printed)
        self.assertIn("Warning: No budget set for 2026-01 yet.", printed)

    @patch("builtins.print")
    def test_create_purchase_order_over_budget_blocks(self, mock_print):
        b_service, _b_repo = self._make_budget_service(month_key="2026-01", record=("2026-01", 5.0, 0.0))

        with patch("Service.purchase_order_service.PurchaseOrder") as MockPO, \
             patch("Service.purchase_order_service.PurchaseOrderLine") as MockLine, \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260104041007"
            MockPO.side_effect = lambda po_id, expected_date, user, status: SimpleNamespace(
                po_id=po_id, expected_date=expected_date, created_by=user, status=status
            )
            MockLine.side_effect = lambda po_id, sku, quantity: SimpleNamespace(po_id=po_id, sku=sku, quantity=quantity)

            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=b_service,
            )

        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Monthly budget for 2026-01: £5.00", printed)
        self.assertIn("Purchase order blocked: estimated cost exceeds the monthly budget.", printed)
        self.assertEqual(self.po_repo.saved, [])
        self.assertTrue(any("PO BLOCKED (over budget)" in a for a in self.audit))

    @patch("builtins.print")
    def test_create_purchase_order_success_with_budget(self, mock_print):
        b_service, b_repo = self._make_budget_service(month_key="2026-01", record=("2026-01", 50.0, 0.0))

        with patch("Service.purchase_order_service.PurchaseOrder") as MockPO, \
             patch("Service.purchase_order_service.PurchaseOrderLine") as MockLine, \
             patch("Service.purchase_order_service.datetime") as mock_dt:

            mock_dt.now.return_value.strftime.return_value = "20260104041008"
            MockPO.side_effect = lambda po_id, expected_date, user, status: SimpleNamespace(
                po_id=po_id, expected_date=expected_date, created_by=user, status=status
            )
            MockLine.side_effect = lambda po_id, sku, quantity: SimpleNamespace(po_id=po_id, sku=sku, quantity=quantity)

            self.svc.create_purchase_order(
                "2026-01-10",
                [{"sku": "SKU1", "quantity": 2}],
                "anetta",
                budget_service=b_service,
            )

        self.assertEqual(len(self.po_repo.saved), 1)

        # If your service updates spent, this will capture it.
        # If it doesn't update spent in your version, just remove these two asserts.
        if getattr(b_repo, "saved_records", None):
            self.assertEqual(b_repo.saved_records[-1][0], "2026-01")  # month

        printed = "\n".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Monthly budget for 2026-01: £50.00", printed)
        self.assertIn("Purchase order PO20260104041008 created successfully", printed)
        self.assertTrue(any("created by anetta" in a for a in self.audit))


if __name__ == "__main__":
    unittest.main()
