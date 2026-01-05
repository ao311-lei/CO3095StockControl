# File: src/tests/tf146/test/whitebox/concolic/test_concolic.py
#
# White-Box (Concolic Testing) test cases for ONLY the code I wrote.
#
# Concolic = CONCrete + symbOLIC:
# - I execute the program with concrete inputs
# - I choose those inputs using the path conditions (like symbolic execution)
# - Each test targets a specific path/branch in my code
#
# Style matches my labs:
# - unittest
# - REAL repos
# - TEMP text files (so I never touch src/data/*)
# - No extra frameworks

import unittest
import os

# -------------------------
# My Models
# -------------------------
from model.product import Product
from model.return_item import ReturnItem
from model.supplier import Supplier

# -------------------------
# My Repos (real repos + temp files)
# -------------------------
from Repo.return_repo import ReturnRepo
from Repo.supplier_repo import SupplierRepo
from Repo.supplier_product_repo import SupplierProductRepo

# shared dependency repo (not authored by me, but used to run my code realistically)
from Repo.product_repo import ProductRepo

# -------------------------
# My Services
# -------------------------
from Service.dashboard_chart_service import DashboardChartService
from Service.return_service import ReturnService
from Service.supplier_catalogue_service import SupplierCatalogueService
from Service.supplier_service import SupplierService

# Dependency written by another member (used only to execute my paths)
from Service.stock_service import StockService
import Service.stock_service as stock_service_module  # redirect AUDIT_FILE


def _safe_remove(path):
    if os.path.exists(path):
        os.remove(path)


# =====================================================
# CONCOLIC: model/product.py (mine)
# status_text()
# I run concrete inputs that force each path condition.
# =====================================================
class TestConcolic_ProductModel(unittest.TestCase):
    def test_concrete_path_active_true(self):
        # Concolic target path condition: active == True
        p = Product("SKU1", "N", "D", 1, 1.0, "Cat", active=True)
        self.assertEqual("ACTIVE", p.status_text())

    def test_concrete_path_active_false(self):
        # Concolic target path condition: active == False
        p = Product("SKU2", "N", "D", 1, 1.0, "Cat", active=False)
        self.assertEqual("INACTIVE", p.status_text())


# =====================================================
# CONCOLIC: model/return_item.py (mine)
# Single path constructor (no branches).
# =====================================================
class TestConcolic_ReturnItemModel(unittest.TestCase):
    def test_concrete_constructor_path(self):
        r = ReturnItem(10, "SKU10", 5, "sealed", "REJECTED", "reason")
        self.assertEqual("SKU10", r.sku)
        self.assertEqual(5, r.quantity)


# =====================================================
# CONCOLIC: model/supplier.py (mine)
# __str__()
# I force ACTIVE / INACTIVE output paths with concrete values.
# =====================================================
class TestConcolic_SupplierModel(unittest.TestCase):
    def test_concrete_str_active(self):
        s = Supplier("SUP1", "Name", "07000", "a@b.com", active=True)
        self.assertIn("ACTIVE", str(s))

    def test_concrete_str_inactive(self):
        s = Supplier("SUP2", "Name", "07000", "a@b.com", active=False)
        self.assertIn("INACTIVE", str(s))


# =====================================================
# CONCOLIC: Repo/return_repo.py (mine)
# __init__ has 2 paths: file exists vs file missing.
# save_return: concrete write/read verification.
# =====================================================
class TestConcolic_ReturnRepo(unittest.TestCase):
    def setUp(self):
        self.returns_file = "tmp_returns_concolic.txt"
        _safe_remove(self.returns_file)

    def tearDown(self):
        _safe_remove(self.returns_file)

    def test_concrete_init_file_missing_path(self):
        # Path condition: file missing triggers FileNotFoundError branch
        repo = ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_concrete_init_file_exists_path(self):
        # Path condition: file exists triggers normal try path
        open(self.returns_file, "w").close()
        repo = ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_concrete_save_return_path(self):
        repo = ReturnRepo(filename=self.returns_file)
        r = ReturnItem(1, "SKU1", 2, "sealed", "ADDED_TO_STOCK", "ok")
        repo.save_return(r)

        with open(self.returns_file, "r") as f:
            content = f.read()
        self.assertIn("SKU1", content)
        self.assertIn("ADDED_TO_STOCK", content)


# =====================================================
# CONCOLIC: Repo/supplier_repo.py (mine)
# I choose concrete file contents to force:
# - blank line continue
# - default fields
# - INACTIVE status
# - find_by_id found / not found
# - update_supplier success / failure
# =====================================================
class TestConcolic_SupplierRepo(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_concolic.txt"
        _safe_remove(self.suppliers_file)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_concrete_load_file_missing_path(self):
        # Path condition: file missing -> repo creates file
        repo = SupplierRepo(filename=self.suppliers_file)
        self.assertTrue(os.path.exists(self.suppliers_file))
        self.assertEqual([], repo.get_all())

    def test_concrete_load_blank_defaults_inactive_paths(self):
        with open(self.suppliers_file, "w") as f:
            f.write("\n")  # blank line -> continue
            f.write("SUP1, Supplier One\n")  # defaults -> ACTIVE
            f.write("SUP2, Supplier Two, 07000, two@x.com, INACTIVE\n")  # inactive

        repo = SupplierRepo(filename=self.suppliers_file)
        all_sups = repo.get_all()
        self.assertEqual(2, len(all_sups))
        self.assertTrue(all_sups[0].active)
        self.assertFalse(all_sups[1].active)

    def test_concrete_find_by_id_paths(self):
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1, Supplier One, , , ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)
        self.assertIsNotNone(repo.find_by_id("SUP1"))     # found
        self.assertIsNone(repo.find_by_id("MISSING"))     # not found

    def test_concrete_update_supplier_paths(self):
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1, Supplier One, , , ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)

        # update success
        self.assertTrue(repo.update_supplier(Supplier("SUP1", "NewName", "", "", True)))

        # update fail
        self.assertFalse(repo.update_supplier(Supplier("SUPX", "Name", "", "", True)))


# =====================================================
# CONCOLIC: Repo/supplier_product_repo.py (mine)
# Concrete file contents to force:
# - blank line -> continue
# - invalid line -> continue
# - valid line -> append
# add_link new/duplicate
# remove_link removed/not removed
# =====================================================
class TestConcolic_SupplierProductRepo(unittest.TestCase):
    def setUp(self):
        self.links_file = "tmp_supplier_products_concolic.txt"
        _safe_remove(self.links_file)

    def tearDown(self):
        _safe_remove(self.links_file)

    def test_concrete_init_file_missing_path(self):
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(os.path.exists(self.links_file))

    def test_concrete_load_paths_blank_invalid_valid(self):
        with open(self.links_file, "w") as f:
            f.write("\n")           # blank -> continue
            f.write("BADLINE\n")     # invalid -> continue
            f.write("SUP1,SKU1\n")   # valid -> append

        repo = SupplierProductRepo(filename=self.links_file)
        self.assertEqual([("SUP1", "SKU1")], repo.load_all_links())

    def test_concrete_add_link_paths(self):
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(repo.add_link("SUP1", "SKU1"))    # new
        self.assertFalse(repo.add_link("SUP1", "SKU1"))   # duplicate

    def test_concrete_remove_link_paths(self):
        repo = SupplierProductRepo(filename=self.links_file)
        repo.save_all_links([("SUP1", "SKU1"), ("SUP2", "SKU2")])

        self.assertTrue(repo.remove_link("SUP1", "SKU1"))     # removed
        self.assertFalse(repo.remove_link("SUPX", "SKUX"))    # not removed


# =====================================================
# CONCOLIC: Service/dashboard_chart_service.py (mine)
# Using real ProductRepo with a temp file, and only valid int quantities
# (because ProductRepo.load_products() requires int(parts[3])).
#
# Concolic idea here:
# - I execute the method with concrete products that force specific paths:
#   qty==0, qty<=threshold, qty>threshold, inactive skip, category empty vs normal
# =====================================================
class TestConcolic_DashboardChartService(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_concolic_dashboard.txt"
        _safe_remove(self.products_file)
        self.product_repo = ProductRepo(filename=self.products_file)

    def tearDown(self):
        _safe_remove(self.products_file)

    def test_concrete_paths_empty_products(self):
        svc = DashboardChartService(self.product_repo)
        lines = svc.build_dashboard_chart_lines(threshold=5)
        self.assertIn("(No categories found)", "\n".join(lines))

    def test_concrete_paths_mixed_products(self):
        with open(self.products_file, "w") as f:
            f.write("A,ProdA,Desc,0,1.0,,ACTIVE\n")           # out of stock, uncategorised
            f.write("B,ProdB,Desc,3,1.0,Food,ACTIVE\n")       # low stock
            f.write("C,ProdC,Desc,10,1.0,Food,ACTIVE\n")      # in stock
            f.write("D,ProdD,Desc,25,1.0,Drinks,INACTIVE\n")  # inactive -> skipped

        self.product_repo.load_products()
        svc = DashboardChartService(self.product_repo)

        status = svc.get_inventory_status_counts(threshold=5)
        self.assertEqual(1, status["out_of_stock"])
        self.assertEqual(1, status["low_stock"])
        self.assertEqual(1, status["in_stock"])

        counts = svc.get_category_counts()
        self.assertEqual(2, counts["Food"])
        self.assertEqual(1, counts["Uncategorised"])


# =====================================================
# CONCOLIC: Service/return_service.py (mine)
# Real ProductRepo + ReturnRepo + real StockService (dependency).
# I redirect StockService audit file to temp.
#
# Concolic targets: I choose concrete inputs that force each major path:
# - sku empty
# - product not found
# - product inactive
# - quantity not int
# - qty <= 0
# - condition not accepted
# - success path (accepted + stock updated)
# =====================================================
class TestConcolic_ReturnService(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_concolic_return.txt"
        self.returns_file = "tmp_returns_concolic_return.txt"
        self.audit_file = "tmp_audit_concolic_stock.txt"

        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

        stock_service_module.AUDIT_FILE = self.audit_file

        self.product_repo = ProductRepo(filename=self.products_file)
        self.return_repo = ReturnRepo(filename=self.returns_file)
        self.stock_service = StockService(self.product_repo)

        self.svc = ReturnService(self.product_repo, self.stock_service, self.return_repo)

    def tearDown(self):
        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

    def _write_product_line(self, sku, name, desc, qty, price, category, status="ACTIVE"):
        with open(self.products_file, "a") as f:
            cat = category if category is not None else ""
            f.write(f"{sku},{name},{desc},{qty},{price},{cat},{status}\n")

    def test_concrete_path_sku_empty(self):
        self.assertEqual("SKU cannot be empty", self.svc.process_return("", 1, "sealed"))

    def test_concrete_path_product_not_found(self):
        msg = self.svc.process_return("MISSING", 1, "sealed")
        self.assertIn("Product not found", msg)
        with open(self.returns_file, "r") as f:
            content = f.read()
        self.assertIn("MISSING", content)
        self.assertIn("REJECTED", content)

    def test_concrete_path_product_inactive(self):
        self._write_product_line("SKU1", "P1", "D", 5, 1.0, "Cat", status="INACTIVE")
        self.product_repo.load_products()

        msg = self.svc.process_return("SKU1", 1, "sealed")
        self.assertIn("inactive", msg.lower())

    def test_concrete_path_quantity_not_int(self):
        self._write_product_line("SKU2", "P2", "D", 5, 1.0, "Cat", status="ACTIVE")
        self.product_repo.load_products()

        self.assertEqual("Quantity must be a whole number", self.svc.process_return("SKU2", "abc", "sealed"))

    def test_concrete_path_qty_leq_zero(self):
        self._write_product_line("SKU3", "P3", "D", 5, 1.0, "Cat", status="ACTIVE")
        self.product_repo.load_products()

        self.assertEqual("Quantity must be greater than 0", self.svc.process_return("SKU3", 0, "sealed"))

    def test_concrete_path_condition_not_accepted(self):
        self._write_product_line("SKU4", "P4", "D", 5, 1.0, "Cat", status="ACTIVE")
        self.product_repo.load_products()

        msg = self.svc.process_return("SKU4", 1, "damaged")
        self.assertIn("NOT added to stock", msg)

    def test_concrete_path_success(self):
        self._write_product_line("SKU5", "P5", "D", 5, 1.0, "Cat", status="ACTIVE")
        self.product_repo.load_products()

        msg = self.svc.process_return("SKU5", 2, "sealed")
        self.assertIn("Return accepted", msg)

        self.product_repo.load_products()
        p = self.product_repo.find_by_sku("SKU5")
        self.assertEqual(7, int(p.quantity))


# =====================================================
# CONCOLIC: Service/supplier_catalogue_service.py (mine)
# Real SupplierRepo + SupplierProductRepo + ProductRepo (dependency), all temp files.
# I choose concrete inputs to force each path:
# empty inputs / supplier not found / inactive / product not found / inactive /
# duplicate link / unlink removed vs missing / view catalogue paths
# =====================================================
class TestConcolic_SupplierCatalogueService(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_concolic_catalogue.txt"
        self.links_file = "tmp_links_concolic_catalogue.txt"
        self.products_file = "tmp_products_concolic_catalogue.txt"

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

    def _write_supplier_line(self, supplier_id, name, status="ACTIVE"):
        with open(self.suppliers_file, "a") as f:
            f.write(f"{supplier_id},{name},,,{status}\n")
        self.supplier_repo.load_suppliers()

    def _write_product_line(self, sku, name, qty, price, category, status="ACTIVE"):
        with open(self.products_file, "a") as f:
            cat = category if category is not None else ""
            f.write(f"{sku},{name},Desc,{qty},{price},{cat},{status}\n")
        self.product_repo.load_products()

    def test_concrete_path_empty_inputs(self):
        msg = self.svc.link_product_to_supplier("", "SKU1")
        self.assertIn("cannot be empty", msg.lower())

    def test_concrete_path_supplier_not_found(self):
        self._write_product_line("SKU1", "P", 1, 1.0, "Cat", status="ACTIVE")
        self.assertEqual("Supplier not found.", self.svc.link_product_to_supplier("SUP1", "SKU1"))

    def test_concrete_path_supplier_inactive(self):
        self._write_supplier_line("SUP1", "S", status="INACTIVE")
        self._write_product_line("SKU1", "P", 1, 1.0, "Cat", status="ACTIVE")
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_concrete_path_product_not_found(self):
        self._write_supplier_line("SUP1", "S", status="ACTIVE")
        self.assertEqual("Product not found.", self.svc.link_product_to_supplier("SUP1", "MISSING"))

    def test_concrete_path_product_inactive(self):
        self._write_supplier_line("SUP1", "S", status="ACTIVE")
        self._write_product_line("SKU1", "P", 1, 1.0, "Cat", status="INACTIVE")
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_concrete_path_duplicate_link(self):
        self._write_supplier_line("SUP1", "S", status="ACTIVE")
        self._write_product_line("SKU1", "P", 1, 1.0, "Cat", status="ACTIVE")

        self.assertIn("successfully", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())
        self.assertIn("already linked", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

    def test_concrete_path_unlink_removed_and_missing(self):
        self._write_supplier_line("SUP1", "S", status="ACTIVE")
        self._write_product_line("SKU1", "P", 1, 1.0, "Cat", status="ACTIVE")

        self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertIn("removed", self.svc.unlink_product_from_supplier("SUP1", "SKU1").lower())
        self.assertIn("does not exist", self.svc.unlink_product_from_supplier("SUP1", "SKU1").lower())

    def test_concrete_view_paths(self):
        # empty id
        products, err = self.svc.view_supplier_catalogue("")
        self.assertIsNone(products)
        self.assertIsNotNone(err)

        # supplier not found
        products2, err2 = self.svc.view_supplier_catalogue("SUP_NOT_FOUND")
        self.assertIsNone(products2)
        self.assertIn("not found", err2.lower())

        # append vs skip
        self._write_supplier_line("SUP1", "S", status="ACTIVE")
        self._write_product_line("SKU1", "P", 1, 1.0, "Cat", status="ACTIVE")
        self.link_repo.add_link("SUP1", "SKU1")
        self.link_repo.add_link("SUP1", "SKU_MISSING")

        prods, err3 = self.svc.view_supplier_catalogue("SUP1")
        self.assertIsNone(err3)
        self.assertEqual(1, len(prods))


# =====================================================
# CONCOLIC: Service/supplier_service.py (mine)
# Real SupplierRepo (temp file). Concrete inputs chosen to force each path.
# =====================================================
class TestConcolic_SupplierService(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_concolic_service.txt"
        _safe_remove(self.suppliers_file)
        self.repo = SupplierRepo(filename=self.suppliers_file)
        self.svc = SupplierService(self.repo)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_concrete_create_supplier_paths(self):
        self.assertEqual("Supplier ID cannot be empty", self.svc.create_supplier("", "Name"))
        self.assertEqual("Supplier name cannot be empty", self.svc.create_supplier("SUP1", ""))

        msg = self.svc.create_supplier("SUP1", "Supplier One", "07000", "a@b.com")
        self.assertIn("successfully", msg.lower())

        msg_dup = self.svc.create_supplier("SUP1", "Again", "07000", "x@y.com")
        self.assertIn("already exists", msg_dup.lower())

    def test_concrete_update_supplier_paths(self):
        self.assertEqual("Supplier ID cannot be empty", self.svc.update_supplier("", "N"))
        self.assertEqual("Supplier not found", self.svc.update_supplier("MISSING", "N"))

        self.svc.create_supplier("SUP1", "OldName", "111", "old@x.com")
        msg = self.svc.update_supplier("SUP1", " NewName ", " 222 ", " new@x.com ")
        self.assertIn("updated successfully", msg.lower())

        s = self.repo.find_by_id("SUP1")
        self.assertEqual("NewName", s.name)

        old_name = s.name
        msg2 = self.svc.update_supplier("SUP1", "   ", "   ", "   ")
        self.assertIn("updated successfully", msg2.lower())
        self.assertEqual(old_name, self.repo.find_by_id("SUP1").name)

    def test_concrete_deactivate_supplier_paths(self):
        self.assertEqual("Supplier ID cannot be empty", self.svc.deactivate_supplier(""))
        self.assertEqual("Supplier not found", self.svc.deactivate_supplier("MISSING"))

        self.svc.create_supplier("SUP1", "Supplier One", "111", "a@b.com")
        msg = self.svc.deactivate_supplier("SUP1")
        self.assertIn("deactivated successfully", msg.lower())

        msg2 = self.svc.deactivate_supplier("SUP1")
        self.assertIn("already inactive", msg2.lower())


if __name__ == "__main__":
    unittest.main()
