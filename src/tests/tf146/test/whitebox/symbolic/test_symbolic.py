# File: src/tests/tf146/test/whitebox/symbolic/test_symbolic.py
#
# WHITE-BOX TESTING — SYMBOLIC EXECUTION / PATH TESTING (unittest)
#
# What I’m doing in this file:
# - I read through the code I wrote and identified the key decisions (if/else checks).
# - For each decision outcome, I wrote at least one test that forces that exact path.
# - I treat inputs like “symbols” and pick concrete values that satisfy each path condition (PC).
#
# Important practical choices I made (based on our lab style):
# - I use REAL repositories and REAL services, but all file I/O goes into TEMP text files.
# - This means my tests never modify src/data/* and they run cleanly on other machines.
# - Some of my services depend on StockService (written by someone else). I only use it
#   as a dependency to allow my code paths to run. I’m not claiming I tested StockService logic.
# - StockService writes audit logs, so I redirect its AUDIT_FILE to a temp file too.

import unittest
import os

# -------------------------
# Models I wrote
# -------------------------
from model.product import Product
from model.return_item import ReturnItem
from model.supplier import Supplier

# -------------------------
# Repos I wrote (plus ProductRepo as a shared dependency)
# -------------------------
from Repo.return_repo import ReturnRepo
from Repo.supplier_repo import SupplierRepo
from Repo.supplier_product_repo import SupplierProductRepo
from Repo.product_repo import ProductRepo  # shared dependency (I use it as a real component)

# -------------------------
# Services I wrote
# -------------------------
from Service.dashboard_chart_service import DashboardChartService
from Service.return_service import ReturnService
from Service.supplier_catalogue_service import SupplierCatalogueService
from Service.supplier_service import SupplierService

# -------------------------
# Dependency service (not written by me)
# -------------------------
from Service.stock_service import StockService
import Service.stock_service as stock_service_module  # used only to redirect AUDIT_FILE safely


# =====================================================
# Helper: safe cleanup for temp files
# =====================================================
def _safe_remove(path: str) -> None:
    """
    Small helper I use throughout this file so I don’t repeat os.path.exists checks.
    It avoids test failures if a file doesn’t exist yet.
    """
    if os.path.exists(path):
        os.remove(path)


# =====================================================
# SYMBOLIC: Product.status_text()
#
# I identified two path conditions in status_text():
#  PC1: active == True  -> returns "ACTIVE"
#  PC2: active == False -> returns "INACTIVE"
#
# Symbolic idea:
# - Treat 'active' as a symbolic boolean.
# - Create one concrete test input for each truth value.
# =====================================================
class TestSymbolic_ProductModel(unittest.TestCase):
    def test_pc_active_true(self):
        # PC: active == True
        p = Product("SKU1", "Name", "Desc", 1, 1.0, "Cat", active=True)

        # Observable behaviour: return string is "ACTIVE"
        self.assertEqual("ACTIVE", p.status_text())

    def test_pc_active_false(self):
        # PC: active == False
        p = Product("SKU2", "Name", "Desc", 1, 1.0, "Cat", active=False)

        # Observable behaviour: return string is "INACTIVE"
        self.assertEqual("INACTIVE", p.status_text())


# =====================================================
# SYMBOLIC: ReturnItem constructor
#
# This class has no branching logic in __init__ (it just assigns fields),
# so there is effectively only one path to test.
# =====================================================
class TestSymbolic_ReturnItemModel(unittest.TestCase):
    def test_pc_single_path_constructor(self):
        # PC: constructor path (no decisions)
        r = ReturnItem("RET1", "SKU1", 2, "sealed", "ADDED_TO_STOCK", "ok")

        # Observable behaviour: fields are stored exactly as passed in
        self.assertEqual("RET1", r.return_id)
        self.assertEqual("SKU1", r.sku)
        self.assertEqual(2, r.quantity)


# =====================================================
# SYMBOLIC: Supplier.__str__()
#
# I identified two path conditions in __str__ (based on status formatting):
#  PC1: active == True  -> output contains "ACTIVE"
#  PC2: active == False -> output contains "INACTIVE"
# =====================================================
class TestSymbolic_SupplierModel(unittest.TestCase):
    def test_pc_supplier_active_true(self):
        # PC: active == True
        s = Supplier("SUP1", "Supplier", "07000", "a@b.com", active=True)

        # Observable behaviour: string representation mentions ACTIVE
        self.assertIn("ACTIVE", str(s))

    def test_pc_supplier_active_false(self):
        # PC: active == False
        s = Supplier("SUP2", "Supplier", "07000", "a@b.com", active=False)

        # Observable behaviour: string representation mentions INACTIVE
        self.assertIn("INACTIVE", str(s))


# =====================================================
# SYMBOLIC: ReturnRepo.__init__ and save_return()
#
# I identified two paths in __init__:
#  PC1: file missing -> FileNotFoundError branch creates the file
#  PC2: file exists  -> normal read/initialisation path
#
# save_return(): single path (append/write).
# =====================================================
class TestSymbolic_ReturnRepo(unittest.TestCase):
    def setUp(self):
        # I use unique filenames per test class so everything is isolated.
        self.returns_file = "tmp_returns_symbolic.txt"
        _safe_remove(self.returns_file)

    def tearDown(self):
        _safe_remove(self.returns_file)

    def test_pc_init_file_missing(self):
        # PC: returns file does NOT exist before repo initialises
        ReturnRepo(filename=self.returns_file)

        # Observable behaviour: the repo initialisation creates the file
        self.assertTrue(os.path.exists(self.returns_file))

    def test_pc_init_file_exists(self):
        # PC: returns file exists before repo initialises
        open(self.returns_file, "w").close()
        ReturnRepo(filename=self.returns_file)

        # Observable behaviour: file still exists (and init should not crash)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_pc_save_return_single_path(self):
        # PC: save_return called with a valid ReturnItem
        repo = ReturnRepo(filename=self.returns_file)
        r = ReturnItem("RET2", "SKU2", 1, "sealed", "ADDED_TO_STOCK", "ok")
        repo.save_return(r)

        # Observable behaviour: file contains data representing the saved return
        with open(self.returns_file, "r") as f:
            content = f.read()

        self.assertIn("RET2", content)
        self.assertIn("SKU2", content)
        self.assertIn("ADDED_TO_STOCK", content)


# =====================================================
# SYMBOLIC: SupplierRepo
#
# Paths I identified while reading SupplierRepo logic:
#  PC1: file missing -> creates empty file + loads empty list
#  PC2: blank line -> continue (skip)
#  PC3: short line -> defaults for optional fields
#  PC4: status INACTIVE -> active False
#  PC5: find_by_id -> found vs not found
#  PC6: update_supplier -> success vs fail
# =====================================================
class TestSymbolic_SupplierRepo(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_symbolic.txt"
        _safe_remove(self.suppliers_file)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_pc_file_missing(self):
        # PC: suppliers file does NOT exist
        repo = SupplierRepo(filename=self.suppliers_file)

        # Observable behaviour: repo creates file + has no suppliers
        self.assertTrue(os.path.exists(self.suppliers_file))
        self.assertEqual([], repo.get_all())

    def test_pc_blank_and_defaults_and_inactive(self):
        # PC: file contains:
        # - a blank line (should be skipped)
        # - a short line (defaults should be applied)
        # - a full line with INACTIVE status (active should become False)
        with open(self.suppliers_file, "w") as f:
            f.write("\n")  # blank => continue
            f.write("SUP1,Supplier One\n")  # short => defaults ACTIVE, empty phone/email
            f.write("SUP2,Supplier Two,07000,two@x.com,INACTIVE\n")  # INACTIVE => active False

        repo = SupplierRepo(filename=self.suppliers_file)
        all_sups = repo.get_all()

        self.assertEqual(2, len(all_sups))
        self.assertTrue(repo.find_by_id("SUP1").active)
        self.assertFalse(repo.find_by_id("SUP2").active)

    def test_pc_find_by_id_found_and_not_found(self):
        # PC: one supplier exists, and we query both existing and missing IDs
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1,Supplier One,,,ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)

        # found path
        self.assertIsNotNone(repo.find_by_id("SUP1"))

        # not found path
        self.assertIsNone(repo.find_by_id("MISSING"))

    def test_pc_update_supplier_success_and_fail(self):
        # PC: supplier exists -> update True
        # PC: supplier missing -> update False
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1,Supplier One,,,ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)

        self.assertTrue(repo.update_supplier(Supplier("SUP1", "NewName", "", "", True)))
        self.assertFalse(repo.update_supplier(Supplier("SUPX", "Name", "", "", True)))


# =====================================================
# SYMBOLIC: SupplierProductRepo
#
# Paths I identified:
#  PC1: init missing -> creates the file
#  PC2: load_all_links reads blank line -> continue
#  PC3: load_all_links reads invalid line -> continue
#  PC4: load_all_links reads valid line -> append to internal list
#  PC5: add_link -> new True / duplicate False
#  PC6: remove_link -> removed True / not found False
# =====================================================
class TestSymbolic_SupplierProductRepo(unittest.TestCase):
    def setUp(self):
        self.links_file = "tmp_supplier_products_symbolic.txt"
        _safe_remove(self.links_file)

    def tearDown(self):
        _safe_remove(self.links_file)

    def test_pc_init_file_missing(self):
        # PC: link file missing
        SupplierProductRepo(filename=self.links_file)

        # Observable behaviour: file is created
        self.assertTrue(os.path.exists(self.links_file))

    def test_pc_load_all_links_blank_invalid_valid(self):
        # PC: file contains blank line, invalid line, and one valid link line
        with open(self.links_file, "w") as f:
            f.write("\n")          # blank => continue
            f.write("BADLINE\n")   # invalid => continue
            f.write("SUP1,SKU1\n") # valid => parsed

        repo = SupplierProductRepo(filename=self.links_file)
        self.assertEqual([("SUP1", "SKU1")], repo.load_all_links())

    def test_pc_add_link_new_and_duplicate(self):
        # PC: first add_link call is new -> True
        # PC: second add_link call is duplicate -> False
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(repo.add_link("SUP1", "SKU1"))
        self.assertFalse(repo.add_link("SUP1", "SKU1"))

    def test_pc_remove_link_true_and_false(self):
        # PC: remove existing link -> True
        # PC: remove missing link -> False
        repo = SupplierProductRepo(filename=self.links_file)
        repo.save_all_links([("SUP1", "SKU1"), ("SUP2", "SKU2")])

        self.assertTrue(repo.remove_link("SUP1", "SKU1"))
        self.assertFalse(repo.remove_link("SUPX", "SKUX"))


# =====================================================
# SYMBOLIC: DashboardChartService
#
# The main decisions I’m testing here:
#  PC1: repo has no products -> chart shows “(No categories found)”
#  PC2: mix of products -> different buckets/counts depending on qty/threshold/category
#
# Note:
# ProductRepo.load_products() expects quantity to be an int in the file.
# So I only write valid integer quantities in the test data file.
# =====================================================
class TestSymbolic_DashboardChartService(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_symbolic_dashboard.txt"
        _safe_remove(self.products_file)
        self.product_repo = ProductRepo(filename=self.products_file)

    def tearDown(self):
        _safe_remove(self.products_file)

    def test_pc_empty_products(self):
        # PC: product list empty
        svc = DashboardChartService(self.product_repo)
        lines = svc.build_dashboard_chart_lines(threshold=5)

        # Observable behaviour: “No categories” message is shown
        self.assertIn("(No categories found)", "\n".join(lines))

    def test_pc_mixed_products(self):
        # PC: includes:
        # - qty == 0 (out of stock)
        # - qty <= threshold (low stock)
        # - qty > threshold (in stock)
        # - category empty -> Uncategorised
        # - INACTIVE product -> skipped by service counts
        with open(self.products_file, "w") as f:
            f.write("A,ProdA,Desc,0,1.0,,ACTIVE\n")
            f.write("B,ProdB,Desc,3,1.0,Food,ACTIVE\n")
            f.write("C,ProdC,Desc,10,1.0,Food,ACTIVE\n")
            f.write("D,ProdD,Desc,25,1.0,Drinks,INACTIVE\n")

        self.product_repo.load_products()
        svc = DashboardChartService(self.product_repo)

        # Observable behaviour: inventory counts match the expected classifications
        status = svc.get_inventory_status_counts(threshold=5)
        self.assertEqual(1, status["out_of_stock"])  # A
        self.assertEqual(1, status["low_stock"])     # B
        self.assertEqual(1, status["in_stock"])      # C

        # Observable behaviour: category counts ignore inactive and handle empty category
        counts = svc.get_category_counts()
        self.assertEqual(2, counts["Food"])           # B + C
        self.assertEqual(1, counts["Uncategorised"])  # A


# =====================================================
# SYMBOLIC: ReturnService.process_return
#
# Paths I derived from reading process_return():
#  PC1: sku == "" -> early return
#  PC2: product not found -> records REJECTED
#  PC3: product inactive -> records REJECTED
#  PC4: quantity cannot be int -> early return
#  PC5: quantity <= 0 -> early return
#  PC6: condition rejected -> records REJECTED (no stock change)
#  PC7: condition accepted -> records ADDED_TO_STOCK + stock increases
#
# I use real ProductRepo + ReturnRepo and the real StockService dependency.
# I redirect StockService AUDIT_FILE to a temp file so nothing touches src/data/.
# =====================================================
class TestSymbolic_ReturnService(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_symbolic_return.txt"
        self.returns_file = "tmp_returns_symbolic_return.txt"
        self.audit_file = "tmp_audit_stockservice_return.txt"

        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

        # Redirect StockService audit log output for safety
        stock_service_module.AUDIT_FILE = self.audit_file

        self.product_repo = ProductRepo(filename=self.products_file)
        self.return_repo = ReturnRepo(filename=self.returns_file)

        # I use real StockService as a dependency so my ReturnService paths can run
        self.stock_service = StockService(self.product_repo)
        self.svc = ReturnService(self.product_repo, self.stock_service, self.return_repo)

    def tearDown(self):
        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

    def _write_product(self, sku, qty, status="ACTIVE"):
        """
        Helper to seed exactly one product row.
        I reload ProductRepo afterwards so ReturnService can find the product.
        """
        with open(self.products_file, "a") as f:
            f.write(f"{sku},Name,Desc,{qty},1.0,Cat,{status}\n")
        self.product_repo.load_products()

    def test_pc_sku_empty(self):
        # PC: sku == ""
        self.assertEqual("SKU cannot be empty", self.svc.process_return("", 1, "sealed"))

    def test_pc_product_not_found(self):
        # PC: sku does not exist in the repo
        msg = self.svc.process_return("MISSING", 1, "sealed")
        self.assertIn("Product not found", msg)

        # Observable side effect: a REJECTED return should be recorded to returns file
        with open(self.returns_file, "r") as f:
            self.assertIn("REJECTED", f.read())

    def test_pc_product_inactive(self):
        # PC: product exists AND is inactive
        self._write_product("SKU1", 5, status="INACTIVE")

        msg = self.svc.process_return("SKU1", 1, "sealed")
        self.assertIn("inactive", msg.lower())

        # Observable side effect: return should be recorded as REJECTED
        with open(self.returns_file, "r") as f:
            self.assertIn("REJECTED", f.read())

    def test_pc_quantity_not_int(self):
        # PC: int(quantity) conversion fails
        self._write_product("SKU2", 5, status="ACTIVE")

        self.assertEqual(
            "Quantity must be a whole number",
            self.svc.process_return("SKU2", "abc", "sealed")
        )

    def test_pc_quantity_leq_zero(self):
        # PC: quantity <= 0
        self._write_product("SKU3", 5, status="ACTIVE")

        self.assertEqual(
            "Quantity must be greater than 0",
            self.svc.process_return("SKU3", 0, "sealed")
        )

    def test_pc_condition_rejected(self):
        # PC: condition is NOT accepted (e.g. damaged)
        self._write_product("SKU4", 5, status="ACTIVE")

        msg = self.svc.process_return("SKU4", 1, "damaged")
        self.assertIn("NOT added to stock", msg)

        # Observable side effect: return is recorded as REJECTED
        with open(self.returns_file, "r") as f:
            self.assertIn("REJECTED", f.read())

    def test_pc_condition_accepted(self):
        # PC: condition is accepted -> should increase stock and record ADDED_TO_STOCK
        self._write_product("SKU5", 5, status="ACTIVE")

        msg = self.svc.process_return("SKU5", 2, "sealed")
        self.assertIn("Return accepted", msg)

        # Observable side effect: file should contain ADDED_TO_STOCK entry
        with open(self.returns_file, "r") as f:
            self.assertIn("ADDED_TO_STOCK", f.read())

        # Observable side effect: product quantity should increase by 2
        self.product_repo.load_products()
        p = self.product_repo.find_by_sku("SKU5")
        self.assertEqual(7, int(p.quantity))


# =====================================================
# SYMBOLIC: SupplierCatalogueService
#
# Paths I’m covering:
# - Empty input (supplier_id or sku missing)
# - Supplier not found / supplier inactive
# - Product not found / product inactive
# - Link new / link duplicate
# - Unlink success / unlink missing
# - View catalogue: empty id / supplier missing / normal view (skips missing products)
# =====================================================
class TestSymbolic_SupplierCatalogueService(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_symbolic_catalogue.txt"
        self.links_file = "tmp_links_symbolic_catalogue.txt"
        self.products_file = "tmp_products_symbolic_catalogue.txt"

        _safe_remove(self.suppliers_file)
        _safe_remove(self.links_file)
        _safe_remove(self.products_file)

        self.supplier_repo = SupplierRepo(filename=self.suppliers_file)
        self.link_repo = SupplierProductRepo(filename=self.links_file)
        self.product_repo = ProductRepo(filename=self.products_file)

        self.svc = SupplierCatalogueService(self.supplier_repo, self.product_repo, self.link_repo)

    def tearDown(self):
        _safe_remove(self.suppliers_file)
        _safe_remove(self.links_file)
        _safe_remove(self.products_file)

    def _write_supplier(self, supplier_id, status="ACTIVE"):
        """
        Helper to seed a supplier row.
        I reload SupplierRepo after writing so the service can find the supplier.
        """
        with open(self.suppliers_file, "a") as f:
            # Keep the format consistent with what SupplierRepo expects
            f.write(f"{supplier_id},Name,,,{status}\n")
        self.supplier_repo.load_suppliers()

    def _write_product(self, sku, qty, status="ACTIVE"):
        """
        Helper to seed a product row (valid int quantity only).
        I reload ProductRepo after writing so the service can find the product.
        """
        with open(self.products_file, "a") as f:
            f.write(f"{sku},Name,Desc,{qty},1.0,Cat,{status}\n")
        self.product_repo.load_products()

    def test_pc_empty_inputs(self):
        # PC: supplier_id == "" OR sku == ""
        self.assertIn("cannot be empty", self.svc.link_product_to_supplier("", "SKU1").lower())

    def test_pc_supplier_not_found(self):
        # PC: supplier missing
        self._write_product("SKU1", 1, "ACTIVE")
        self.assertEqual("Supplier not found.", self.svc.link_product_to_supplier("SUP1", "SKU1"))

    def test_pc_supplier_inactive(self):
        # PC: supplier exists but inactive
        self._write_supplier("SUP1", "INACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_pc_product_not_found(self):
        # PC: product missing
        self._write_supplier("SUP1", "ACTIVE")
        self.assertEqual("Product not found.", self.svc.link_product_to_supplier("SUP1", "MISSING"))

    def test_pc_product_inactive(self):
        # PC: product exists but inactive
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "INACTIVE")
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_pc_duplicate_link(self):
        # PC: first link is new (success), second link is duplicate
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")

        self.assertIn("successfully", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())
        self.assertIn("already linked", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_pc_unlink_success_and_missing(self):
        # PC: unlink existing -> success, unlink again -> missing
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")

        self.svc.link_product_to_supplier("SUP1", "SKU1")

        self.assertIn("removed", self.svc.unlink_product_from_supplier("SUP1", "SKU1").lower())
        self.assertIn("does not exist", self.svc.unlink_product_from_supplier("SUP1", "SKU1").lower())

    def test_pc_view_paths(self):
        # PC: empty supplier_id
        prods, err = self.svc.view_supplier_catalogue("")
        self.assertIsNone(prods)
        self.assertIsNotNone(err)

        # PC: supplier does not exist
        prods2, err2 = self.svc.view_supplier_catalogue("SUP_NOT_FOUND")
        self.assertIsNone(prods2)
        self.assertIn("not found", err2.lower())

        # PC: normal view
        # also includes a missing product link which should be skipped internally
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")

        self.link_repo.add_link("SUP1", "SKU1")
        self.link_repo.add_link("SUP1", "MISSING")  # skip branch inside view

        prods3, err3 = self.svc.view_supplier_catalogue("SUP1")
        self.assertIsNone(err3)
        self.assertEqual(1, len(prods3))


# =====================================================
# SYMBOLIC: SupplierService
#
# Paths I’m covering here:
# - create_supplier: empty id / empty name / success / duplicate
# - update_supplier: empty id / not found / success / blanks ignored
# - deactivate_supplier: empty id / not found / success / already inactive
# =====================================================
class TestSymbolic_SupplierService(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_symbolic_service.txt"
        _safe_remove(self.suppliers_file)

        self.repo = SupplierRepo(filename=self.suppliers_file)
        self.svc = SupplierService(self.repo)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_pc_create_paths(self):
        # PC: empty supplier id
        self.assertEqual("Supplier ID cannot be empty", self.svc.create_supplier("", "Name"))

        # PC: empty supplier name
        self.assertEqual("Supplier name cannot be empty", self.svc.create_supplier("SUP1", ""))

        # PC: success
        self.assertIn("successfully", self.svc.create_supplier("SUP1", "Supplier One", "07000", "a@b.com").lower())

        # PC: duplicate
        self.assertIn("already exists", self.svc.create_supplier("SUP1", "Again").lower())

    def test_pc_update_paths(self):
        # PC: empty id
        self.assertEqual("Supplier ID cannot be empty", self.svc.update_supplier("", "N"))

        # PC: supplier not found
        self.assertEqual("Supplier not found", self.svc.update_supplier("MISSING", "N"))

        # Seed one supplier so I can test the successful update paths
        self.svc.create_supplier("SUP1", "OldName", "111", "old@x.com")

        # PC: success update with trimming/cleanup
        self.assertIn(
            "updated successfully",
            self.svc.update_supplier("SUP1", " NewName ", " 222 ", " new@x.com ").lower()
        )

        # PC: update called with blanks (should keep old values)
        old_name = self.repo.find_by_id("SUP1").name
        self.assertIn("updated successfully", self.svc.update_supplier("SUP1", "   ", "   ", "   ").lower())
        self.assertEqual(old_name, self.repo.find_by_id("SUP1").name)

    def test_pc_deactivate_paths(self):
        # PC: empty id
        self.assertEqual("Supplier ID cannot be empty", self.svc.deactivate_supplier(""))

        # PC: supplier not found
        self.assertEqual("Supplier not found", self.svc.deactivate_supplier("MISSING"))

        # Seed supplier then deactivate
        self.svc.create_supplier("SUP1", "Supplier One", "111", "a@b.com")

        # PC: success deactivate
        self.assertIn("deactivated successfully", self.svc.deactivate_supplier("SUP1").lower())

        # PC: already inactive
        self.assertIn("already inactive", self.svc.deactivate_supplier("SUP1").lower())


if __name__ == "__main__":
    unittest.main()
