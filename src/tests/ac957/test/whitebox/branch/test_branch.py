import os
import tempfile
import unittest
from unittest.mock import MagicMock

from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService

from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService

from Service.product_service import ProductService


# =========================================================
# BudgetRepo — Branch Tests (REAL repo, temp file)
# =========================================================

class TestBudgetRepoBranchCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "budgets.txt")
        self.repo = BudgetRepo(filename=self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load_budget_record_empty_file(self):
        self.assertEqual(self.repo.load_budget_record(), (None, None, None))

    def test_load_budget_record_invalid_format(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("bad_line\n")
        self.assertEqual(self.repo.load_budget_record(), (None, None, None))

    def test_load_budget_record_month_only(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("2026-01|\n")
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)
        self.assertEqual(spent, 0.0)

    def test_load_budget_record_month_and_budget_no_spent(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("2026-01|500\n")
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertEqual(budget, 500.0)
        self.assertEqual(spent, 0.0)

    def test_save_budget_record_budget_none(self):
        self.repo.save_budget_record("2026-01", None, 25.0)
        month, budget, spent = self.repo.load_budget_record()
        self.assertEqual(month, "2026-01")
        self.assertIsNone(budget)
        self.assertEqual(spent, 25.0)

    def test_current_month_key_format(self):
        key = self.repo.current_month_key()
        self.assertRegex(key, r"^\d{4}-\d{2}$")


# =========================================================
# BudgetService — Branch Tests (REAL repo/service, temp file)
# =========================================================

class TestBudgetServiceBranchCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "budgets.txt")
        self.repo = BudgetRepo(filename=self.path)
        self.service = BudgetService(self.repo)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_set_monthly_budget_empty(self):
        self.assertEqual(self.service.set_monthly_budget("   "), "Budget cannot be empty.")

    def test_set_monthly_budget_not_number(self):
        self.assertEqual(self.service.set_monthly_budget("abc"), "Budget must be a number.")

    def test_set_monthly_budget_negative(self):
        self.assertEqual(self.service.set_monthly_budget("-1"), "Budget cannot be negative.")

    def test_set_monthly_budget_zero_valid(self):
        msg = self.service.set_monthly_budget("0")
        self.assertIn("Monthly budget saved for", msg)

    def test_set_monthly_budget_formats_currency(self):
        msg = self.service.set_monthly_budget(" 500 ")
        self.assertIn("£500.00", msg)

    def test_view_monthly_budget_none_set(self):
        msg = self.service.view_monthly_budget()
        self.assertIn("No budget set for", msg)
        self.assertIsNone(self.service.get_budget_remaining())

    def test_view_monthly_budget_with_spent_and_remaining(self):
        month_key = self.repo.current_month_key()
        self.repo.save_budget_record(month_key, 500.0, 190.0)
        msg = self.service.view_monthly_budget()
        self.assertIn("£500.00", msg)
        self.assertIn("Spent so far: £190.00", msg)
        self.assertIn("Remaining: £310.00", msg)
        self.assertEqual(self.service.get_budget_remaining(), 310.0)

    def test_add_spend_no_budget_set(self):
        self.assertEqual(self.service.add_spend("25"), "No budget set.")

    def test_add_spend_updates_spent(self):
        self.service.set_monthly_budget("500")
        self.service.add_spend("25")
        _, _, spent = self.repo.load_budget_record()
        self.assertEqual(spent, 25.0)

    def test_add_spend_accumulates(self):
        self.service.set_monthly_budget("500")
        self.service.add_spend("25")
        self.service.add_spend("40")
        _, _, spent = self.repo.load_budget_record()
        self.assertEqual(spent, 65.0)

    def test_add_spend_invalid_amount_raises(self):
        self.service.set_monthly_budget("500")
        with self.assertRaises(ValueError):
            self.service.add_spend("abc")


# =========================================================
# FavouriteRepo — Branch Tests (REAL repo, temp file)
# =========================================================

class TestFavouriteRepoBranchCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "favourites.txt")
        self.repo = FavouriteRepo(filename=self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load_all_empty(self):
        self.assertEqual(self.repo.load_all(), [])

    def test_load_all_strips_spaces(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("  anetta  ,  SKU001  \n\nbob,SKU002\n")
        self.assertEqual(self.repo.load_all(), [("anetta", "SKU001"), ("bob", "SKU002")])

    def test_add_favourite_no_duplicate(self):
        self.repo.add_favourite("anetta", "SKU001")
        self.repo.add_favourite("anetta", "SKU001")
        self.assertEqual(self.repo.load_all().count(("anetta", "SKU001")), 1)

    def test_remove_favourite_removes(self):
        self.repo.save_all([("anetta", "SKU001")])
        self.repo.remove_favourite("anetta", "SKU001")
        self.assertFalse(self.repo.is_favourite("anetta", "SKU001"))

    def test_get_favourites_returns_user_skus(self):
        self.repo.save_all([("anetta", "SKU001"), ("bob", "SKU002"), ("anetta", "SKU003")])
        self.assertEqual(self.repo.get_favourites("anetta"), ["SKU001", "SKU003"])


# =========================================================
# FavouriteService — Branch Tests (REAL repo + MagicMock deps)
# =========================================================

class TestFavouriteServiceBranchCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "favourites.txt")
        self.fav_repo = FavouriteRepo(filename=self.path)

        # Product repo dependency: MagicMock
        self.p1 = {"sku": "SKU001"}
        self.p2 = {"sku": "SKU002"}
        self.product_repo = MagicMock()
        self.product_repo.find_by_sku.side_effect = lambda sku: {"SKU001": self.p1, "SKU002": self.p2}.get(sku)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_get_username_no_auth_service(self):
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=None)
        self.assertIsNone(svc._get_username())

    def test_get_username_auth_no_user(self):
        auth = MagicMock()
        auth.current_user = None
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertIsNone(svc._get_username())

    def test_get_username_auth_with_user(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc._get_username(), "anetta")

    def test_favourite_product_not_logged_in(self):
        auth = MagicMock()
        auth.current_user = None
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc.favourite_product("SKU001"), "You must be logged in to favourite products.")

    def test_favourite_product_empty_sku(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc.favourite_product("   "), "SKU cannot be empty.")

    def test_favourite_product_product_not_found(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc.favourite_product("SKU999"), "Product not found.")

    def test_favourite_product_add_success_then_already(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)

        self.assertEqual(svc.favourite_product("SKU001"), "Product added to favourites.")
        self.assertEqual(svc.favourite_product("SKU001"), "This product is already favourited.")

    def test_get_favourites_not_logged_in(self):
        auth = MagicMock()
        auth.current_user = None
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        products, err = svc.get_favourites()
        self.assertIsNone(products)
        self.assertEqual(err, "You must be logged in to view favourites.")

    def test_get_favourites_filters_missing_products(self):
        self.fav_repo.save_all([("anetta", "SKU001"), ("anetta", "SKU404"), ("anetta", "SKU002")])

        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user

        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        products, err = svc.get_favourites()

        self.assertIsNone(err)
        self.assertEqual(products, [self.p1, self.p2])

    def test_unfavourite_product_not_logged_in(self):
        auth = MagicMock()
        auth.current_user = None
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc.unfavourite_product("SKU001"), "You must be logged in to unfavourite products.")

    def test_unfavourite_product_empty_sku(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc.unfavourite_product("   "), "SKU cannot be empty.")

    def test_unfavourite_product_not_in_favourites(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user
        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        self.assertEqual(svc.unfavourite_product("SKU001"), "This product is not in your favourites.")

    def test_unfavourite_product_remove_success(self):
        user = MagicMock()
        user.username = "anetta"
        auth = MagicMock()
        auth.current_user = user

        svc = FavouriteService(self.fav_repo, self.product_repo, auth_service=auth)
        svc.favourite_product("SKU001")

        self.assertEqual(svc.unfavourite_product("SKU001"), "Product removed from favourites.")
        self.assertFalse(self.fav_repo.is_favourite("anetta", "SKU001"))


# =========================================================
# ProductService — Branch Tests (MagicMock repo + MagicMock products)
#   - No ProductRepo tests (per your requirement)
#   - Still hits every branch in ProductService methods you listed
# =========================================================

class TestProductServiceBranchCoverage(unittest.TestCase):
    def setUp(self):
        # Fake repo (ONLY what ProductService calls)
        self.product_repo = MagicMock()
        self.category_repo = MagicMock()

        # Build some “product objects” using MagicMock (no dummy classes)
        self.p1 = MagicMock()
        self.p1.sku = "SKU001"
        self.p1.name = "Apple"
        self.p1.description = "Fresh red apple"
        self.p1.category = "Fruit"
        self.p1.quantity = 5
        self.p1.price = 1.5
        self.p1.active = True

        self.p2 = MagicMock()
        self.p2.sku = "SKU002"
        self.p2.name = "Banana"
        self.p2.description = "Yellow banana"
        self.p2.category = "Fruit"
        self.p2.quantity = 20
        self.p2.price = 0.75
        self.p2.active = True

        self.p3 = MagicMock()
        self.p3.sku = "SKU003"
        self.p3.name = "Detergent"
        self.p3.description = "Laundry soap"
        self.p3.category = "Cleaning"
        self.p3.quantity = 2
        self.p3.price = 4.0
        self.p3.active = True

        self.inactive = MagicMock()
        self.inactive.sku = "SKU999"
        self.inactive.name = "Old"
        self.inactive.description = "Inactive"
        self.inactive.category = "Other"
        self.inactive.quantity = 1
        self.inactive.price = 9.99
        self.inactive.active = False

        self.all_products = [self.p1, self.p2, self.p3, self.inactive]

        # repo.get_all_products used by several methods
        self.product_repo.get_all_products.return_value = list(self.all_products)

        # repo.find_by_sku used by several methods
        def _find_by_sku(sku):
            lookup = {p.sku: p for p in self.all_products}
            return lookup.get(sku)

        self.product_repo.find_by_sku.side_effect = _find_by_sku

        # Create service
        self.service = ProductService(self.product_repo, self.category_repo)

        # Capture audit writes
        self.audit = []
        self.service.write_audit = lambda msg: self.audit.append(msg)

        # Track saves
        self.product_repo.save_product.reset_mock()

    # -------------------------
    # deactivate_product
    # -------------------------
    def test_deactivate_empty_sku(self):
        self.assertEqual(self.service.deactivate_product(" "), "SKU cannot be empty")
        self.product_repo.find_by_sku.assert_not_called()

    def test_deactivate_product_not_found(self):
        self.assertEqual(self.service.deactivate_product("NOPE"), "Product not found")

    def test_deactivate_already_inactive(self):
        self.assertEqual(self.service.deactivate_product("SKU999"), "Product is already INACTIVE")

    def test_deactivate_success_saves_and_audits(self):
        msg = self.service.deactivate_product("SKU001", user="anetta")
        self.assertEqual(msg, "Product deactivated successfully")
        self.assertFalse(self.p1.active)
        self.product_repo.save_product.assert_called_once_with(self.p1)
        self.assertTrue(any("ACTION=PRODUCT_DEACTIVATE" in a for a in self.audit))

    # -------------------------
    # reactivate_product
    # -------------------------
    def test_reactivate_empty_sku(self):
        self.assertEqual(self.service.reactivate_product(" "), "SKU cannot be empty")

    def test_reactivate_not_found(self):
        self.assertEqual(self.service.reactivate_product("NOPE"), "Product not found")

    def test_reactivate_already_active(self):
        self.assertEqual(self.service.reactivate_product("SKU001"), "Product is already ACTIVE")

    def test_reactivate_success_saves(self):
        # Make sure product is inactive going into the branch
        self.inactive.active = False
        msg = self.service.reactivate_product("SKU999")
        self.assertEqual(msg, "Product reactivated successfully")
        self.assertTrue(self.inactive.active)
        self.product_repo.save_product.assert_called_with(self.inactive)

    # -------------------------
    # search_products
    # -------------------------
    def test_search_products_empty_query_returns_empty_list(self):
        self.assertEqual(self.service.search_products("   "), [])

    def test_search_products_matches_sku(self):
        got = self.service.search_products("sku001")
        self.assertEqual(got, [self.p1])

    def test_search_products_matches_name(self):
        got = self.service.search_products("banana")
        self.assertEqual(got, [self.p2])

    def test_search_products_matches_description(self):
        got = self.service.search_products("laundry")
        self.assertEqual(got, [self.p3])

    # -------------------------
    # filter_products
    # -------------------------
    def test_filter_products_no_filters_returns_all(self):
        got = self.service.filter_products()
        self.assertEqual(got, self.all_products)

    def test_filter_products_category_filters_case_and_spaces(self):
        got = self.service.filter_products(category=" fruit ")
        self.assertEqual(got, [self.p1, self.p2])

    def test_filter_products_max_qty_valid(self):
        got = self.service.filter_products(max_qty="5")
        # qty <= 5 => p1 (5), p3 (2), inactive (1)
        self.assertEqual(got, [self.p1, self.p3, self.inactive])

    def test_filter_products_max_qty_invalid_ignored(self):
        got = self.service.filter_products(max_qty="abc")
        self.assertEqual(got, self.all_products)

    def test_filter_products_sort_by_name(self):
        got = self.service.filter_products(sort_by="name")
        # Apple, Banana, Detergent, Old
        self.assertEqual(got, [self.p1, self.p2, self.p3, self.inactive])

    def test_filter_products_sort_by_quantity(self):
        got = self.service.filter_products(sort_by="quantity")
        # qty: inactive(1), p3(2), p1(5), p2(20)
        self.assertEqual(got, [self.inactive, self.p3, self.p1, self.p2])

    def test_filter_products_sort_by_price(self):
        got = self.service.filter_products(sort_by="price")
        # price: p2(0.75), p1(1.5), p3(4.0), inactive(9.99)
        self.assertEqual(got, [self.p2, self.p1, self.p3, self.inactive])

    # -------------------------
    # estimate_restock_cost_for_sku
    # -------------------------
    def test_estimate_restock_empty_sku(self):
        est, err = self.service.estimate_restock_cost_for_sku(" ", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "SKU cannot be empty.")

    def test_estimate_restock_target_not_int(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU001", "x")
        self.assertIsNone(est)
        self.assertEqual(err, "Target stock level must be a whole number.")

    def test_estimate_restock_target_negative(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU001", -1)
        self.assertIsNone(est)
        self.assertEqual(err, "Target stock level cannot be negative.")

    def test_estimate_restock_product_not_found(self):
        est, err = self.service.estimate_restock_cost_for_sku("NOPE", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "Product not found.")

    def test_estimate_restock_inactive_product(self):
        est, err = self.service.estimate_restock_cost_for_sku("SKU999", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "This product is INACTIVE. Reactivate it before planning restock.")

    def test_estimate_restock_invalid_product_data(self):
        bad = MagicMock()
        bad.sku = "BAD"
        bad.name = "Bad"
        bad.quantity = "x"
        bad.price = "y"
        bad.active = True

        # Extend repo lookup + list
        self.all_products.append(bad)
        self.product_repo.get_all_products.return_value = list(self.all_products)

        def _find_by_sku(sku):
            lookup = {p.sku: p for p in self.all_products}
            return lookup.get(sku)

        self.product_repo.find_by_sku.side_effect = _find_by_sku

        est, err = self.service.estimate_restock_cost_for_sku("BAD", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "Product data is invalid (quantity/price).")

    def test_estimate_restock_already_at_or_above_target(self):
        # p2 qty=20, target=10 => already at/above
        est, err = self.service.estimate_restock_cost_for_sku("SKU002", 10)
        self.assertIsNone(est)
        self.assertEqual(err, "This product is already at or above the target stock level.")

    def test_estimate_restock_success(self):
        # p1 qty=5 price=1.5 target=10 => buy 5 => 7.5
        est, err = self.service.estimate_restock_cost_for_sku("SKU001", 10)
        self.assertIsNone(err)
        self.assertEqual(est["units_to_buy"], 5)
        self.assertEqual(est["estimated_cost"], 7.5)

    # -------------------------
    # estimate_restock_cost_for_multiple_skus
    # -------------------------
    def test_estimate_multiple_mixed(self):
        sku_targets = [("SKU001", 10), ("NOPE", 10), ("SKU999", 10), ("SKU002", 10)]
        breakdown, total, errors = self.service.estimate_restock_cost_for_multiple_skus(sku_targets)

        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0]["sku"], "SKU001")
        self.assertEqual(total, 7.5)
        self.assertEqual(len(errors), 3)

    # -------------------------
    # view_all_products_with_status
    # -------------------------
    def test_view_all_products_with_status_default_low_stock_5(self):
        results = self.service.view_all_products_with_status()  # low_stock=5
        status_map = {p.sku: status for (p, status) in results}

        self.assertEqual(status_map["SKU999"], "INACTIVE")     # inactive wins
        self.assertEqual(status_map["SKU001"], "LOW STOCK")    # qty=5
        self.assertEqual(status_map["SKU003"], "LOW STOCK")    # qty=2
        self.assertEqual(status_map["SKU002"], "IN STOCK")     # qty=20

    def test_view_all_products_with_status_out_of_stock(self):
        # add an active qty=0 product using MagicMock
        p0 = MagicMock()
        p0.sku = "SKU000"
        p0.name = "Zero"
        p0.description = "None"
        p0.category = "Other"
        p0.quantity = 0
        p0.price = 1.0
        p0.active = True

        products = self.all_products + [p0]
        self.product_repo.get_all_products.return_value = products

        results = self.service.view_all_products_with_status(low_stock=5)
        status_map = {p.sku: status for (p, status) in results}
        self.assertEqual(status_map["SKU000"], "OUT OF STOCK")

    def test_view_all_products_with_status_custom_threshold(self):
        # with low_stock=1, qty=2 and 5 are IN STOCK (not low)
        results = self.service.view_all_products_with_status(low_stock=1)
        status_map = {p.sku: status for (p, status) in results}

        self.assertEqual(status_map["SKU999"], "INACTIVE")
        self.assertEqual(status_map["SKU001"], "IN STOCK")
        self.assertEqual(status_map["SKU003"], "IN STOCK")

    # -------------------------
    # get_low_stock_products
    # -------------------------
    def test_get_low_stock_products_invalid_threshold_returns_none(self):
        self.assertIsNone(self.service.get_low_stock_products("abc"))

    def test_get_low_stock_products_negative_threshold_returns_none(self):
        self.assertIsNone(self.service.get_low_stock_products(-1))

    def test_get_low_stock_products_returns_only_active_and_qty_le_threshold(self):
        low = self.service.get_low_stock_products(5)
        # threshold=5 => p1(5), p3(2) ; ignore inactive and high qty
        self.assertEqual(low, [self.p1, self.p3])

    def test_get_low_stock_products_ignores_inactive_products(self):
        low = self.service.get_low_stock_products(100)
        self.assertNotIn(self.inactive, low)

    def test_get_low_stock_products_skips_broken_quantity_data(self):
        badq = MagicMock()
        badq.sku = "BADQ"
        badq.name = "BadQ"
        badq.description = "Bad"
        badq.category = "Other"
        badq.quantity = "X"  # will fail int()
        badq.price = 1.0
        badq.active = True

        products = self.all_products + [badq]
        self.product_repo.get_all_products.return_value = products

        low = self.service.get_low_stock_products(10)
        self.assertNotIn(badq, low)


if __name__ == "__main__":
    unittest.main()
