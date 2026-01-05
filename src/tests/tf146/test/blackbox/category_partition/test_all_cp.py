"""
Partition Table (summary of input categories I test)
------------------------------------------------------------
Product (model)
- active: {True, False}
- __str__ output: {contains key fields}

Supplier (model)
- active: {True, False}
- optional fields: {empty, filled}

ReturnService.process_return
- sku: {empty, valid}
- product existence: {not found, found}
- product active: {inactive, active}
- quantity: {non-int, <=0, positive}
- condition: {accepted, not accepted}
- stock update: {success, fails/exception}

SupplierCatalogueService
- supplier_id/sku: {empty, non-empty}
- supplier: {not found, inactive, active}
- product: {not found, inactive, active}
- link: {new, duplicate}
- unlink: {missing, exists}
- view catalogue: {empty id, supplier missing, normal}

SupplierService
- supplier_id: {empty, valid, duplicate}
- name: {empty, valid}
- deactivate: {missing, already inactive, success}

ProductRepo (I claim)
- init/load: {missing file -> empty}
- remove_by_sku: {exists, missing}
- update_product: {exists, missing}
- get_all_products: {empty, non-empty}

ProductService (I claim)
- add_new_product: {empty sku, empty name, bad qty, neg qty, bad price, neg price, duplicate sku, success}
- update_product: {empty sku, missing sku, empty name, bad qty, neg qty, bad price, neg price, success}
- remove_product: {empty sku, missing sku, success}
- get_low_stock_products: {bad threshold, neg threshold, valid threshold with: inactive skip, bad qty skip, include <= threshold}
- get_dashboard_summary: {empty products, CRITICAL, WARNING, HEALTHY}
"""

import os
import tempfile
import unittest
# -------------------------
# Imports from project
# -------------------------
from model.product import Product
from model.return_item import ReturnItem
from model.supplier import Supplier

from Repo.return_repo import ReturnRepo
from Repo.supplier_repo import SupplierRepo
from Repo.supplier_product_repo import SupplierProductRepo
from Repo.product_repo import ProductRepo

from Service.return_service import ReturnService
from Service.supplier_catalogue_service import SupplierCatalogueService
from Service.supplier_service import SupplierService
from Service.dashboard_chart_service import DashboardChartService
from Service.product_service import ProductService

# StockService is part of project (not written by me)
from Service.stock_service import StockService

# Redirect ProductService audit log safely
import Service.product_service as product_service_module
import Service.stock_service as stock_service_module

from unittest.mock import patch
from model.menus import Menus


# Helper: real temp-file paths for each test class

class TempFilesMixin:
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        base = self.tmpdir.name

        self.products_file = os.path.join(base, "products_test.txt")
        self.suppliers_file = os.path.join(base, "suppliers_test.txt")
        self.links_file = os.path.join(base, "supplier_products_test.txt")
        self.returns_file = os.path.join(base, "returns_test.txt")
        self.audit_file = os.path.join(base, "audit_log_test.txt")

    def tearDown(self):
        self.tmpdir.cleanup()



# MODELS: Category Partition (blackbox)
#---------------------------------------------
class TestBB_CP_Models(unittest.TestCase):

    def test_product_status_text_active_true(self):
        # Partition: active = True
        p = Product("SKU1", "Milk", "Desc", 1, 1.50, "Dairy", active=True)
        self.assertEqual("ACTIVE", p.status_text())

    def test_product_status_text_active_false(self):
        # Partition: active = False
        p = Product("SKU2", "Bread", "Desc", 1, 0.99, "Bakery", active=False)
        self.assertEqual("INACTIVE", p.status_text())

    def test_product_str_contains_key_fields(self):
        # Partition: __str__ output contains key fields (robust: assertIn)
        p = Product("SKU3", "Eggs", "Desc", 12, 2.25, "Food", active=True)
        text = str(p)
        self.assertIn("SKU3", text)
        self.assertIn("Eggs", text)
        self.assertIn("12", text)
        self.assertIn("£", text)
        self.assertIn("ACTIVE", text)

    def test_supplier_str_active_optional_empty(self):
        # Partition: active=True, optional fields empty
        s = Supplier("SUP1", "Acme", phone="", email="", active=True)
        text = str(s)
        self.assertIn("SUP1", text)
        self.assertIn("Acme", text)
        self.assertIn("ACTIVE", text)

    def test_supplier_str_inactive_optional_filled(self):
        # Partition: active=False, optional fields filled
        s = Supplier("SUP2", "Best Supplies", phone="07123456789", email="test@example.com", active=False)
        text = str(s)
        self.assertIn("SUP2", text)
        self.assertIn("Best Supplies", text)
        self.assertIn("07123456789", text)
        self.assertIn("test@example.com", text)
        self.assertIn("INACTIVE", text)

    def test_return_item_typical_values_stored(self):
        # Partition: typical constructor values
        r = ReturnItem("R1", "SKU1", 1, "NEW", "ADDED_TO_STOCK", "sealed")
        self.assertEqual("R1", r.return_id)
        self.assertEqual("SKU1", r.sku)
        self.assertEqual(1, r.quantity)
        self.assertEqual("NEW", r.condition)
        self.assertEqual("ADDED_TO_STOCK", r.decision)
        self.assertEqual("sealed", r.reason)



# REPOS: Category Partition (real repos + temp files)
# -------------------------------------------------------
class TestBB_CP_Repos(TempFilesMixin, unittest.TestCase):

    def test_return_repo_missing_file_created_on_init(self):
        # Partition: returns file missing before init
        self.assertFalse(os.path.exists(self.returns_file))
        ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_return_repo_save_return_writes_expected_format(self):
        # Partition: normal save_return writes correct line format
        repo = ReturnRepo(filename=self.returns_file)
        r = ReturnItem("R1", "SKU1", 2, "NEW", "ADDED_TO_STOCK", "sealed")
        repo.save_return(r)

        with open(self.returns_file, "r") as f:
            line = f.readline().strip()

        self.assertIn("R1|SKU1|2|NEW|ADDED_TO_STOCK|sealed", line)

    def test_supplier_repo_missing_file_created_and_loads_empty(self):
        # Partition: suppliers file missing before init
        self.assertFalse(os.path.exists(self.suppliers_file))
        repo = SupplierRepo(filename=self.suppliers_file)
        self.assertTrue(os.path.exists(self.suppliers_file))
        self.assertEqual([], repo.get_all())

    def test_supplier_repo_load_minimal_fields_defaults(self):
        # Partition: line has only id and name -> defaults apply
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1,Acme\n")

        repo = SupplierRepo(filename=self.suppliers_file)
        s = repo.find_by_id("SUP1")
        self.assertIsNotNone(s)
        self.assertEqual("", s.phone)
        self.assertEqual("", s.email)
        self.assertTrue(s.active)

    def test_supplier_product_repo_add_link_unique_and_duplicate(self):
        # Partition: link {new, duplicate}
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(repo.add_link("SUP1", "SKU1"))   # new
        self.assertFalse(repo.add_link("SUP1", "SKU1"))  # duplicate

    def test_product_repo_init_missing_file_empty(self):
        # Partition: init/load missing file -> empty
        repo = ProductRepo(filename=self.products_file)
        self.assertEqual([], repo.get_all_products())

    def test_product_repo_remove_by_sku_exists_and_missing(self):
        # Partition: remove_by_sku {exists, missing}
        repo = ProductRepo(filename=self.products_file)

        # Seed using repo method (real file persistence)
        repo.add_product(Product("SKU10", "A", "D", 1, 1.0, None, True))
        repo.add_product(Product("SKU11", "B", "D", 2, 2.0, None, True))

        self.assertTrue(repo.remove_by_sku("SKU10"))      # exists
        self.assertFalse(repo.remove_by_sku("MISSING"))   # missing

    def test_product_repo_update_product_exists_and_missing(self):
        # Partition: update_product {exists, missing}
        repo = ProductRepo(filename=self.products_file)
        repo.add_product(Product("SKU20", "Old", "OldD", 1, 1.0, None, True))

        self.assertFalse(repo.update_product("MISSING", "N", "D", 1, 1.0, None))
        self.assertTrue(repo.update_product("SKU20", "New", "NewD", 5, 9.99, "Cat"))

        p = repo.find_by_sku("SKU20")
        self.assertEqual("New", p.name)
        self.assertEqual(5, p.quantity)


# SERVICES: Category Partition (real repos + temp files)
# --------------------------------------------------------------------

class TestBB_CP_ReturnService(TempFilesMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()

        # Real repos + temp files
        self.product_repo = ProductRepo(filename=self.products_file)
        self.return_repo = ReturnRepo(filename=self.returns_file)
        self.stock_service = StockService(self.product_repo)


        # redirect StockService audit file so tests don't depend on src/data existing
        self._tmpdir = tempfile.TemporaryDirectory()
        self.audit_file = os.path.join(self._tmpdir.name, "audit_log_test.txt")
        stock_service_module.AUDIT_FILE = self.audit_file



        # Seed one active product + one inactive product
        self.product_repo.add_product(Product("SKU1", "Active", "D", 10, 1.0, "C", True))
        self.product_repo.add_product(Product("SKU2", "Inactive", "D", 10, 1.0, "C", False))

        self.svc = ReturnService(self.product_repo, self.stock_service, self.return_repo)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_process_return_partitions(self):
        # sku: empty
        self.assertEqual("SKU cannot be empty", self.svc.process_return("", 1, "sealed"))

        # product existence: not found
        msg = self.svc.process_return("MISSING", 1, "sealed")
        self.assertIn("Product not found", msg)

        # product active: inactive
        msg = self.svc.process_return("SKU2", 1, "sealed")
        self.assertIn("inactive", msg.lower())

        # quantity: non-int
        self.assertEqual("Quantity must be a whole number", self.svc.process_return("SKU1", "abc", "sealed"))

        # quantity: <= 0
        self.assertEqual("Quantity must be greater than 0", self.svc.process_return("SKU1", 0, "sealed"))

        # condition: not accepted
        msg = self.svc.process_return("SKU1", 1, "damaged")
        self.assertIn("NOT added to stock", msg)

        # normal success: accepted condition + stock increases
        msg = self.svc.process_return("SKU1", 2, "sealed")
        self.assertIn("Return accepted", msg)


class TestBB_CP_SupplierCatalogueService(TempFilesMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.supplier_repo = SupplierRepo(filename=self.suppliers_file)
        self.product_repo = ProductRepo(filename=self.products_file)
        self.link_repo = SupplierProductRepo(filename=self.links_file)

        # Seed suppliers: active + inactive
        self.supplier_repo.add_supplier(Supplier("SUP1", "ActiveSupp", active=True))
        self.supplier_repo.add_supplier(Supplier("SUP2", "InactiveSupp", active=False))

        # Seed products: active + inactive
        self.product_repo.add_product(Product("SKU1", "ActiveP", "D", 1, 1.0, "C", True))
        self.product_repo.add_product(Product("SKU2", "InactiveP", "D", 1, 1.0, "C", False))

        self.svc = SupplierCatalogueService(self.supplier_repo, self.product_repo, self.link_repo)

    def test_link_partitions(self):
        # supplier_id/sku: empty
        self.assertIn("cannot be empty", self.svc.link_product_to_supplier("", "SKU1").lower())
        self.assertIn("cannot be empty", self.svc.link_product_to_supplier("SUP1", "").lower())

        # supplier: not found
        self.assertIn("not found", self.svc.link_product_to_supplier("SUP-NO", "SKU1").lower())

        # supplier: inactive
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP2", "SKU1").lower())

        # product: not found
        self.assertIn("product not found", self.svc.link_product_to_supplier("SUP1", "SKU-NO").lower())

        # product: inactive
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP1", "SKU2").lower())

        # link: new then duplicate
        self.assertIn("successfully", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())
        self.assertIn("already linked", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_unlink_partitions(self):
        # unlink: missing
        self.assertIn("does not exist", self.svc.unlink_product_from_supplier("SUP1", "SKU1").lower())

        # unlink: exists
        self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertIn("removed", self.svc.unlink_product_from_supplier("SUP1", "SKU1").lower())

    def test_view_catalogue_partitions(self):
        # view: empty id
        products, err = self.svc.view_supplier_catalogue("")
        self.assertIsNone(products)
        self.assertIsNotNone(err)

        # view: supplier missing
        products, err = self.svc.view_supplier_catalogue("SUP-NO")
        self.assertIsNone(products)
        self.assertIn("not found", err.lower())

        # view: normal
        self.svc.link_product_to_supplier("SUP1", "SKU1")
        products, err = self.svc.view_supplier_catalogue("SUP1")
        self.assertIsNone(err)
        self.assertEqual(1, len(products))
        self.assertEqual("SKU1", products[0].sku)


class TestBB_CP_SupplierService(TempFilesMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.repo = SupplierRepo(filename=self.suppliers_file)
        self.svc = SupplierService(self.repo)

        # seed one supplier for duplicate/deactivate partitions
        self.repo.add_supplier(Supplier("SUP1", "Existing", active=True))

    def test_create_supplier_partitions(self):
        # supplier_id: empty
        self.assertIn("cannot be empty", self.svc.create_supplier("", "Name").lower())

        # name: empty
        self.assertIn("cannot be empty", self.svc.create_supplier("SUPX", "").lower())

        # supplier_id: duplicate
        self.assertIn("already exists", self.svc.create_supplier("SUP1", "NewName").lower())

        # normal success
        self.assertIn("successfully", self.svc.create_supplier("SUP2", "NewSupp", "0700", "x@y.com").lower())

    def test_deactivate_partitions(self):
        # deactivate: missing
        self.assertIn("not found", self.svc.deactivate_supplier("MISSING").lower())

        # deactivate: success
        self.assertIn("deactivated", self.svc.deactivate_supplier("SUP1").lower())

        # deactivate: already inactive
        self.assertIn("already", self.svc.deactivate_supplier("SUP1").lower())


class TestBB_CP_DashboardChartService(TempFilesMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.product_repo = ProductRepo(filename=self.products_file)

    def test_dashboard_public_methods_partitions(self):
        # category counts: empty (also triggers "(No categories found)" later)
        svc = DashboardChartService(self.product_repo)
        joined = "\n".join(svc.build_dashboard_chart_lines(threshold=5))
        self.assertIn("(No categories found)", joined)

        # Add mixed products to cover main public behaviours
        self.product_repo.add_product(Product("A", "A", "D", 0, 1.0, None, True))          # out of stock + uncategorised
        self.product_repo.add_product(Product("B", "B", "D", 5, 1.0, "Food", True))        # low stock
        self.product_repo.add_product(Product("C", "C", "D", 6, 1.0, "Food", True))        # in stock
        self.product_repo.add_product(Product("D", "D", "D", 25, 1.0, "Drinks", True))     # 21+ bucket
        self.product_repo.add_product(Product("E", "E", "D", 1, 1.0, "X", False))          # inactive skipped

        status = svc.get_inventory_status_counts(threshold=5)
        self.assertEqual(1, status["out_of_stock"])
        self.assertEqual(1, status["low_stock"])
        self.assertEqual(2, status["in_stock"])

        buckets = svc.get_stock_bucket_counts()
        self.assertEqual(1, buckets["0"])
        self.assertEqual(1, buckets["1-5"])
        self.assertEqual(1, buckets["6-20"])
        self.assertEqual(1, buckets["21+"])



# ProductService (I claim): real ProductRepo + temp files
# --------------------------------------------------------------
class TestBB_CP_ProductService(TempFilesMixin, unittest.TestCase):

    class DummyCategoryRepo:
        # ProductService requires a CategoryRepo parameter,
        # but the claimed methods in my ProductService do not use it.
        pass

    def setUp(self):
        super().setUp()

        # Redirect audit file to temp (so tests never touch src/data/audit_log.txt)
        product_service_module.AUDIT_FILE = self.audit_file

        self.product_repo = ProductRepo(filename=self.products_file)
        self.svc = ProductService(self.product_repo, self.DummyCategoryRepo())

        # Seed one product for duplicate/missing tests
        self.product_repo.add_product(Product("SKU1", "Existing", "D", 10, 1.0, "C", True))

    def test_add_new_product_partitions(self):
        self.assertEqual("SKU cannot be empty", self.svc.add_new_product("", "N", "D", 1, 1.0))
        self.assertEqual("Name cannot be empty", self.svc.add_new_product("SKU2", "", "D", 1, 1.0))
        self.assertEqual("Quantity must be a whole number", self.svc.add_new_product("SKU2", "N", "D", "abc", 1.0))
        self.assertEqual("Quantity cannot be negative", self.svc.add_new_product("SKU2", "N", "D", -1, 1.0))
        self.assertEqual("Price must be a number", self.svc.add_new_product("SKU2", "N", "D", 1, "xyz"))
        self.assertEqual("Price cannot be negative", self.svc.add_new_product("SKU2", "N", "D", 1, -2.0))

        self.assertEqual("That SKU already exists", self.svc.add_new_product("SKU1", "N", "D", 1, 1.0))

        ok = self.svc.add_new_product("SKU3", "New", "Desc", 2, 2.5, "Food", user="tf146")
        self.assertIn("successfully", ok.lower())

    def test_update_product_partitions(self):
        self.assertEqual("SKU cannot be empty", self.svc.update_product("", "N", "D", 1, 1.0, None))
        self.assertEqual("Product not found", self.svc.update_product("MISSING", "N", "D", 1, 1.0, None))
        self.assertEqual("Name cannot be empty", self.svc.update_product("SKU1", "", "D", 1, 1.0, None))
        self.assertEqual("Quantity must be a whole number", self.svc.update_product("SKU1", "N", "D", "abc", 1.0, None))
        self.assertEqual("Quantity cannot be negative", self.svc.update_product("SKU1", "N", "D", -1, 1.0, None))
        self.assertEqual("Price must be a number", self.svc.update_product("SKU1", "N", "D", 1, "xyz", None))
        self.assertEqual("Price cannot be negative", self.svc.update_product("SKU1", "N", "D", 1, -1.0, None))

        ok = self.svc.update_product("SKU1", "Updated", "NewD", 5, 9.99, "Cat", user="tf146")
        self.assertIn("updated successfully", ok.lower())

    def test_remove_product_partitions(self):
        self.assertEqual("SKU cannot be empty", self.svc.remove_product("", user="tf146"))
        self.assertEqual("Product not found", self.svc.remove_product("MISSING", user="tf146"))

        ok = self.svc.remove_product("SKU1", user="tf146")
        self.assertIn("removed successfully", ok.lower())

    def test_get_low_stock_products_partitions(self):
        # Add products to cover: inactive skip, include <= threshold
        self.product_repo.add_product(Product("LOW1", "L", "D", 2, 1.0, "C", True))
        self.product_repo.add_product(Product("INACT", "I", "D", 1, 1.0, "C", False))

        self.assertIsNone(self.svc.get_low_stock_products("abc"))  # bad threshold
        self.assertIsNone(self.svc.get_low_stock_products(-1))     # negative threshold

        low = self.svc.get_low_stock_products(2)
        skus = [p.sku for p in low]
        self.assertIn("LOW1", skus)
        self.assertNotIn("INACT", skus)

    def test_get_dashboard_summary_partitions(self):
        # empty products (use fresh repo/service)
        repo_empty = ProductRepo(filename=os.path.join(self.tmpdir.name, "products_empty.txt"))
        svc_empty = ProductService(repo_empty, self.DummyCategoryRepo())
        summary_empty = svc_empty.get_dashboard_summary(threshold=5)
        self.assertEqual(0, summary_empty["total_products"])
        self.assertEqual(0, summary_empty["low_stock_percent"])
        self.assertEqual(0, summary_empty["out_of_stock_percent"])

        # CRITICAL (out of stock exists)
        repo_crit = ProductRepo(filename=os.path.join(self.tmpdir.name, "products_crit.txt"))
        svc_crit = ProductService(repo_crit, self.DummyCategoryRepo())
        repo_crit.add_product(Product("A", "A", "D", 0, 1.0, "C", True))
        repo_crit.add_product(Product("B", "B", "D", 1, 1.0, "C", True))
        summary_crit = svc_crit.get_dashboard_summary(threshold=5)
        self.assertEqual("CRITICAL", summary_crit["system_status"])

        # WARNING (>=3 low stock, none out of stock)
        repo_warn = ProductRepo(filename=os.path.join(self.tmpdir.name, "products_warn.txt"))
        svc_warn = ProductService(repo_warn, self.DummyCategoryRepo())
        repo_warn.add_product(Product("C", "C", "D", 1, 1.0, "C", True))
        repo_warn.add_product(Product("D", "D", "D", 2, 1.0, "C", True))
        repo_warn.add_product(Product("E", "E", "D", 3, 1.0, "C", True))
        summary_warn = svc_warn.get_dashboard_summary(threshold=5)
        self.assertEqual("WARNING", summary_warn["system_status"])

        # HEALTHY (low stock < 3, none out of stock)
        repo_ok = ProductRepo(filename=os.path.join(self.tmpdir.name, "products_ok.txt"))
        svc_ok = ProductService(repo_ok, self.DummyCategoryRepo())
        repo_ok.add_product(Product("F", "F", "D", 10, 1.0, "C", True))
        repo_ok.add_product(Product("G", "G", "D", 9, 1.0, "C", True))
        summary_ok = svc_ok.get_dashboard_summary(threshold=5)
        self.assertEqual("HEALTHY", summary_ok["system_status"])

class DummyUser:
    """
    Simple dummy user object used only for menu testing.
    I created this to control the role (manager / non-manager)
    without depending on the real AuthService.
    """
    def __init__(self, role):
        self.role = role

    def is_manager(self):
        return self.role in ["MANAGER", "ADMIN"]

    def is_admin(self):
        return self.role == "ADMIN"


def get_printed_output(print_mock):
    """
    Helper function I use to collect everything printed to the console
    so I can assert against visible menu output.
    """
    output = []
    for call in print_mock.call_args_list:
        if call.args:
            output.append(str(call.args[0]))
    return "\n".join(output)


class TestBB_CP_Menus_TF146(unittest.TestCase):
    """
    BLACK-BOX TESTING — CATEGORY PARTITION

    I am testing the menu functions I personally implemented.
    The tests focus only on observable behaviour (printed menu options
    and returned user choices), not internal implementation.

    Category partitions used:
    - current_user role: {non-manager, manager}
    - menu input choice: {valid options, back/exit}
    """

    # ==========================================================
    # view_main_menu
    # ==========================================================

    def test_view_main_menu_non_manager_partition(self):
        """
        Partition tested:
        - current_user is NOT a manager

        Expected behaviour:
        - Manager-only options (e.g. Suppliers) should not be printed
        """
        menus = Menus()
        user = DummyUser("STAFF")

        with patch("builtins.input", return_value="0"), patch("builtins.print") as mock_print:
            choice = menus.view_main_menu(user)

        self.assertEqual(choice, "0")

        output = get_printed_output(mock_print)

        # Options I added should always appear
        self.assertIn("1) Products", output)
        self.assertIn("5) Dashboard", output)
        self.assertIn("6) Returns", output)

        # Manager-only option should not appear
        self.assertNotIn("8) Suppliers", output)

    def test_view_main_menu_manager_partition(self):
        """
        Partition tested:
        - current_user IS a manager

        Expected behaviour:
        - Supplier option should now be visible
        """
        menus = Menus()
        user = DummyUser("MANAGER")

        with patch("builtins.input", return_value="8"), patch("builtins.print") as mock_print:
            choice = menus.view_main_menu(user)

        self.assertEqual(choice, "8")

        output = get_printed_output(mock_print)

        self.assertIn("1) Products", output)
        self.assertIn("5) Dashboard", output)
        self.assertIn("6) Returns", output)
        self.assertIn("8) Suppliers", output)

    # ==========================================================
    # view_products_menu
    # ==========================================================

    def test_view_products_menu_non_manager_partition(self):
        """
        Partition tested:
        - current_user is NOT a manager

        Expected behaviour:
        - Add / Remove / Update / Low stock options should NOT appear
        """
        menus = Menus()
        user = DummyUser("STAFF")

        with patch("builtins.input", return_value="0"), patch("builtins.print") as mock_print:
            choice = menus.view_products_menu(user)

        self.assertEqual(choice, "0")

        output = get_printed_output(mock_print)

        # Always-visible options
        self.assertIn("1) View all products", output)
        self.assertIn("2) Search products", output)
        self.assertIn("3) Filter products", output)

        # Manager-only options (added by me) should not appear
        self.assertNotIn("4) Add Product", output)
        self.assertNotIn("5) Remove Product", output)
        self.assertNotIn("6) Update Product", output)
        self.assertNotIn("7) Low Stock Alerts", output)
        self.assertNotIn("9) Set Low Stock Threshold", output)

    def test_view_products_menu_manager_partition(self):
        """
        Partition tested:
        - current_user IS a manager

        Expected behaviour:
        - Manager-only product options should be printed
        """
        menus = Menus()
        user = DummyUser("MANAGER")

        with patch("builtins.input", return_value="9"), patch("builtins.print") as mock_print:
            choice = menus.view_products_menu(user)

        self.assertEqual(choice, "9")

        output = get_printed_output(mock_print)

        self.assertIn("4) Add Product", output)
        self.assertIn("5) Remove Product", output)
        self.assertIn("6) Update Product", output)
        self.assertIn("7) Low Stock Alerts", output)
        self.assertIn("9) Set Low Stock Threshold", output)

    # ==========================================================
    # view_suppliers_menu (entire function written by me)
    # ==========================================================

    def test_view_suppliers_menu_valid_choice_partition(self):
        """
        Partition tested:
        - user enters a valid supplier menu option

        Expected behaviour:
        - function returns the entered choice
        """
        menus = Menus()

        with patch("builtins.input", return_value="3"), patch("builtins.print") as mock_print:
            choice = menus.view_suppliers_menu()

        self.assertEqual(choice, "3")

        output = get_printed_output(mock_print)

        self.assertIn("1) Create supplier", output)
        self.assertIn("2) Update supplier", output)
        self.assertIn("3) Deactivate supplier", output)
        self.assertIn("4) List suppliers", output)
        self.assertIn("5) Supplier product catalogue", output)
        self.assertIn("0) Back", output)

    # ==========================================================
    # view_supplier_catalogue_menu (entire function written by me)
    # ==========================================================

    def test_view_supplier_catalogue_menu_valid_choice_partition(self):
        """
        Partition tested:
        - user selects a valid catalogue menu option

        Expected behaviour:
        - function returns the selected option
        """
        menus = Menus()

        with patch("builtins.input", return_value="2"), patch("builtins.print") as mock_print:
            choice = menus.view_supplier_catalogue_menu()

        self.assertEqual(choice, "2")

        output = get_printed_output(mock_print)

        self.assertIn("1) Link product to supplier", output)
        self.assertIn("2) Unlink product from supplier", output)
        self.assertIn("3) View supplier catalogue", output)
        self.assertIn("0) Back", output)
if __name__ == "__main__":
    unittest.main()
