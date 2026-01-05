# File: src/tests/tf146/test/whitebox/branch/test_branch.py
#
# White-Box (Branch) testing for ONLY the code I wrote.
# I use real repositories + temporary text files so the tests do not touch src/data/*
# Tool/style: unittest + coverage --branch when measuring branch coverage.

import unittest
import os

# =========================
# Imports: Models (mine)
# =========================
from model.product import Product
from model.return_item import ReturnItem
from model.supplier import Supplier

# =========================
# Imports: Repos (mine + shared dependency)
# =========================
from Repo.return_repo import ReturnRepo
from Repo.supplier_repo import SupplierRepo
from Repo.supplier_product_repo import SupplierProductRepo
from Repo.product_repo import ProductRepo  # shared, used as real dependency

# =========================
# Imports: Services (mine + shared dependency)
# =========================
from Service.dashboard_chart_service import DashboardChartService
from Service.return_service import ReturnService
from Service.supplier_catalogue_service import SupplierCatalogueService
from Service.supplier_service import SupplierService
from Service.product_service import ProductService  # shared module (I only test methods I wrote)

# redirect audit file in ProductService + StockService to temp files
import Service.product_service as product_service_module
import Service.stock_service as stock_service_module
from Service.stock_service import StockService  # dependency used by ReturnService

# =====================================================
# helper: safe remove temp files
# =====================================================
def _safe_remove(path):
    if os.path.exists(path):
        os.remove(path)


# =====================================================
# BRANCH TESTS: model/product.py (mine)
# Branches: status_text() -> True/False
# =====================================================
class TestBranch_ProductModel(unittest.TestCase):
    def test_status_text_active_true(self):
        p = Product("SKU1", "N", "D", 1, 1.0, "Cat", active=True)
        self.assertEqual("ACTIVE", p.status_text())

    def test_status_text_active_false(self):
        p = Product("SKU2", "N", "D", 1, 1.0, "Cat", active=False)
        self.assertEqual("INACTIVE", p.status_text())


# =====================================================
# BRANCH TESTS: model/return_item.py (mine)
# No branches -> 1 test
# =====================================================
class TestBranch_ReturnItemModel(unittest.TestCase):
    def test_return_item_init(self):
        r = ReturnItem("RET1", "SKU1", 1, "sealed", "ADDED_TO_STOCK", "OK")
        self.assertEqual("RET1", r.return_id)
        self.assertEqual("SKU1", r.sku)


# =====================================================
# BRANCH TESTS: model/supplier.py (mine)
# Branches: __str__ -> ACTIVE/INACTIVE
# =====================================================
class TestBranch_SupplierModel(unittest.TestCase):
    def test_supplier_str_active(self):
        s = Supplier("SUP1", "Name", "07000", "a@b.com", active=True)
        self.assertIn("ACTIVE", str(s))

    def test_supplier_str_inactive(self):
        s = Supplier("SUP2", "Name", "07000", "a@b.com", active=False)
        self.assertIn("INACTIVE", str(s))


# =====================================================
# BRANCH TESTS: Repo/return_repo.py (mine)
# Branches: __init__ -> file exists / file missing
# =====================================================
class TestBranch_ReturnRepo(unittest.TestCase):
    def setUp(self):
        self.returns_file = "tmp_returns_branch.txt"
        _safe_remove(self.returns_file)

    def tearDown(self):
        _safe_remove(self.returns_file)

    def test_init_file_missing_except_path(self):
        repo = ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_init_file_exists_try_path(self):
        open(self.returns_file, "w").close()
        repo = ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))


# =====================================================
# BRANCH TESTS: Repo/supplier_repo.py (mine)
# Branches:
# - file missing vs normal read
# - blank line continue
# - ACTIVE/INACTIVE status mapping
# - find_by_id found / not found
# - update_supplier True / False
# =====================================================
class TestBranch_SupplierRepo(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_branch.txt"
        _safe_remove(self.suppliers_file)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_load_suppliers_file_missing_branch(self):
        repo = SupplierRepo(filename=self.suppliers_file)
        self.assertTrue(os.path.exists(self.suppliers_file))
        self.assertEqual([], repo.get_all())

    def test_load_suppliers_normal_branch_blank_defaults_inactive(self):
        with open(self.suppliers_file, "w") as f:
            f.write("\n")  # blank -> continue
            f.write("SUP1, Supplier One\n")  # defaults -> ACTIVE
            f.write("SUP2, Supplier Two, 07000, two@x.com, INACTIVE\n")  # inactive -> active False

        repo = SupplierRepo(filename=self.suppliers_file)
        all_sups = repo.get_all()

        self.assertEqual(2, len(all_sups))
        self.assertTrue(all_sups[0].active)
        self.assertFalse(all_sups[1].active)

    def test_find_by_id_found_and_not_found(self):
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1, Supplier One, , , ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)
        self.assertIsNotNone(repo.find_by_id("SUP1"))
        self.assertIsNone(repo.find_by_id("MISSING"))

    def test_update_supplier_true_and_false(self):
        with open(self.suppliers_file, "w") as f:
            f.write("SUP1, Supplier One, , , ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)

        # True branch
        ok = repo.update_supplier(Supplier("SUP1", "NewName", "", "", True))
        self.assertTrue(ok)

        # False branch
        ok2 = repo.update_supplier(Supplier("SUPX", "Name", "", "", True))
        self.assertFalse(ok2)


# =====================================================
# BRANCH TESTS: Repo/supplier_product_repo.py (mine)
# Branches:
# - __init__ file missing / exists
# - load_all_links: blank continue / invalid continue / valid parse
# - add_link: True / False
# - remove_link: True / False
# - get_products_for_supplier: match / no match
# - get_suppliers_for_product: match / no match
# =====================================================
class TestBranch_SupplierProductRepo(unittest.TestCase):
    def setUp(self):
        self.links_file = "tmp_supplier_products_branch.txt"
        _safe_remove(self.links_file)

    def tearDown(self):
        _safe_remove(self.links_file)

    def test_init_file_missing_branch(self):
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(os.path.exists(self.links_file))

    def test_init_file_exists_branch(self):
        open(self.links_file, "w").close()
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(os.path.exists(self.links_file))

    def test_load_all_links_branches(self):
        with open(self.links_file, "w") as f:
            f.write("\n")          # blank -> continue
            f.write("BADLINE\n")    # invalid -> continue
            f.write("SUP1,SKU1\n")  # valid parse

        repo = SupplierProductRepo(filename=self.links_file)
        self.assertEqual([("SUP1", "SKU1")], repo.load_all_links())

    def test_add_link_true_and_false(self):
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(repo.add_link("SUP1", "SKU1"))
        self.assertFalse(repo.add_link("SUP1", "SKU1"))

    def test_remove_link_true_and_false(self):
        repo = SupplierProductRepo(filename=self.links_file)
        repo.save_all_links([("SUP1", "SKU1"), ("SUP2", "SKU2")])

        self.assertTrue(repo.remove_link("SUP1", "SKU1"))
        self.assertFalse(repo.remove_link("SUPX", "SKUX"))

    def test_get_products_for_supplier_match_and_no_match(self):
        repo = SupplierProductRepo(filename=self.links_file)
        repo.save_all_links([("SUP1", "SKU1"), ("SUP2", "SKU2")])

        self.assertEqual(["SKU1"], repo.get_products_for_supplier("SUP1"))
        self.assertEqual([], repo.get_products_for_supplier("SUPX"))

    def test_get_suppliers_for_product_match_and_no_match(self):
        repo = SupplierProductRepo(filename=self.links_file)
        repo.save_all_links([("SUP1", "SKU1"), ("SUP2", "SKU2")])

        self.assertEqual(["SUP1"], repo.get_suppliers_for_product("SKU1"))
        self.assertEqual([], repo.get_suppliers_for_product("SKUX"))


# =====================================================
# BRANCH TESTS: Service/dashboard_chart_service.py (mine)
# I use REAL ProductRepo with a temp file.
#
# Branches covered:
# - get_inventory_status_counts: qty==0 / qty<=threshold / else, inactive continue
# - get_stock_bucket_counts: 0 / 1-5 / 6-20 / 21+ , inactive continue
# - get_category_counts: uncategorised / normal, cat exists/not exists
# - build_dashboard_chart_lines: no categories -> len(top)==0 / else
#
# NOTE: ProductRepo.load_products() requires int quantity, so I only write valid ints.
# =====================================================
class TestBranch_DashboardChartService(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_branch_dashboard.txt"
        _safe_remove(self.products_file)
        self.product_repo = ProductRepo(filename=self.products_file)

    def tearDown(self):
        _safe_remove(self.products_file)

    def test_build_dashboard_lines_empty_products_branch(self):
        svc = DashboardChartService(self.product_repo)
        lines = svc.build_dashboard_chart_lines(threshold=5)
        self.assertIn("(No categories found)", "\n".join(lines))

    def test_mixed_products_branches(self):
        with open(self.products_file, "w") as f:
            f.write("A,ProdA,Desc,0,1.0,,ACTIVE\n")           # qty==0 + uncategorised
            f.write("B,ProdB,Desc,3,1.0,Food,ACTIVE\n")       # qty<=threshold
            f.write("C,ProdC,Desc,10,1.0,Food,ACTIVE\n")      # else branch + category exists
            f.write("D,ProdD,Desc,25,1.0,Drinks,ACTIVE\n")    # 21+ bucket
            f.write("E,ProdE,Desc,5,1.0,Snacks,INACTIVE\n")   # inactive -> continue

        self.product_repo.load_products()
        svc = DashboardChartService(self.product_repo)

        status = svc.get_inventory_status_counts(threshold=5)
        self.assertEqual(1, status["out_of_stock"])
        self.assertEqual(1, status["low_stock"])
        self.assertEqual(2, status["in_stock"])  # C + D

        buckets = svc.get_stock_bucket_counts()
        self.assertEqual(1, buckets["0"])
        self.assertEqual(1, buckets["1-5"])   # B (3) and C (10) goes to 6-20, so only B + A? Actually A is 0.
        self.assertEqual(1, buckets["6-20"])  # C (10)
        self.assertEqual(1, buckets["21+"])   # D (25)

        counts = svc.get_category_counts()
        self.assertEqual(2, counts["Food"])           # B + C
        self.assertEqual(1, counts["Uncategorised"])  # A
        self.assertEqual(1, counts["Drinks"])         # D


# =====================================================
# BRANCH TESTS: Service/return_service.py (mine)
# I use REAL ProductRepo + ReturnRepo + REAL StockService (dependency), all temp files.
#
# Branches in process_return:
# - sku empty
# - product not found
# - product inactive
# - quantity int conversion fail / pass
# - qty <= 0 / qty > 0
# - condition accepted / not accepted
# - stock_service success path
# (StockService exception path depends on its implementation; I do not force it here.)
# =====================================================
class TestBranch_ReturnService(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_branch_return.txt"
        self.returns_file = "tmp_returns_branch_return.txt"
        self.audit_file = "tmp_audit_branch_stock.txt"

        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

        # redirect audit file used by StockService
        stock_service_module.AUDIT_FILE = self.audit_file

        self.product_repo = ProductRepo(filename=self.products_file)
        self.return_repo = ReturnRepo(filename=self.returns_file)
        self.stock_service = StockService(self.product_repo)
        self.svc = ReturnService(self.product_repo, self.stock_service, self.return_repo)

    def tearDown(self):
        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

    def _write_product_line(self, sku, qty, status="ACTIVE"):
        with open(self.products_file, "a") as f:
            f.write(f"{sku},Name,Desc,{qty},1.0,Cat,{status}\n")
        self.product_repo.load_products()

    def test_sku_empty_branch(self):
        self.assertEqual("SKU cannot be empty", self.svc.process_return("", 1, "sealed"))

    def test_product_not_found_branch_records(self):
        msg = self.svc.process_return("MISSING", 1, "sealed")
        self.assertIn("Product not found", msg)

        with open(self.returns_file, "r") as f:
            content = f.read()
        self.assertIn("MISSING", content)
        self.assertIn("REJECTED", content)

    def test_product_inactive_branch(self):
        self._write_product_line("SKU1", 5, status="INACTIVE")
        msg = self.svc.process_return("SKU1", 1, "sealed")
        self.assertIn("inactive", msg.lower())

    def test_quantity_not_int_branch(self):
        self._write_product_line("SKU2", 5, status="ACTIVE")
        self.assertEqual("Quantity must be a whole number", self.svc.process_return("SKU2", "abc", "sealed"))

    def test_qty_leq_zero_branch(self):
        self._write_product_line("SKU3", 5, status="ACTIVE")
        self.assertEqual("Quantity must be greater than 0", self.svc.process_return("SKU3", 0, "sealed"))

    def test_condition_not_accepted_branch_records(self):
        self._write_product_line("SKU4", 5, status="ACTIVE")
        msg = self.svc.process_return("SKU4", 1, "damaged")
        self.assertIn("NOT added to stock", msg)

    def test_success_branch_updates_stock(self):
        self._write_product_line("SKU5", 5, status="ACTIVE")
        msg = self.svc.process_return("SKU5", 2, "sealed")
        self.assertIn("Return accepted", msg)

        self.product_repo.load_products()
        p = self.product_repo.find_by_sku("SKU5")
        self.assertEqual(7, int(p.quantity))


# =====================================================
# BRANCH TESTS: Service/supplier_catalogue_service.py (mine)
# Real repos with temp files:
# - empty input branch
# - supplier not found / inactive
# - product not found / inactive
# - add_link True / False
# - remove_link True / False
# - view paths (empty id / supplier missing / append vs skip)
# =====================================================
class TestBranch_SupplierCatalogueService(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_branch_catalogue.txt"
        self.links_file = "tmp_links_branch_catalogue.txt"
        self.products_file = "tmp_products_branch_catalogue.txt"

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
        with open(self.suppliers_file, "a") as f:
            f.write(f"{supplier_id},Supplier,,,{status}\n")
        self.supplier_repo.load_suppliers()

    def _write_product(self, sku, qty, status="ACTIVE"):
        with open(self.products_file, "a") as f:
            f.write(f"{sku},Prod,Desc,{qty},1.0,Cat,{status}\n")
        self.product_repo.load_products()

    def test_link_empty_inputs_branch(self):
        msg = self.svc.link_product_to_supplier("", "SKU1")
        self.assertIn("cannot be empty", msg.lower())

    def test_link_supplier_not_found_branch(self):
        self._write_product("SKU1", 1, "ACTIVE")
        msg = self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertEqual("Supplier not found.", msg)

    def test_link_supplier_inactive_branch(self):
        self._write_supplier("SUP1", "INACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")
        msg = self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertIn("inactive", msg.lower())

    def test_link_product_not_found_branch(self):
        self._write_supplier("SUP1", "ACTIVE")
        msg = self.svc.link_product_to_supplier("SUP1", "MISSING")
        self.assertEqual("Product not found.", msg)

    def test_link_product_inactive_branch(self):
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "INACTIVE")
        msg = self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertIn("inactive", msg.lower())

    def test_add_link_true_and_false_branches(self):
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")

        msg1 = self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertIn("successfully", msg1.lower())

        msg2 = self.svc.link_product_to_supplier("SUP1", "SKU1")
        self.assertIn("already linked", msg2.lower())

    def test_unlink_true_and_false_branches(self):
        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")
        self.svc.link_product_to_supplier("SUP1", "SKU1")

        msg_removed = self.svc.unlink_product_from_supplier("SUP1", "SKU1")
        self.assertIn("removed", msg_removed.lower())

        msg_missing = self.svc.unlink_product_from_supplier("SUP1", "SKU1")
        self.assertIn("does not exist", msg_missing.lower())

    def test_view_catalogue_branches(self):
        products, err = self.svc.view_supplier_catalogue("")
        self.assertIsNone(products)
        self.assertIsNotNone(err)

        products2, err2 = self.svc.view_supplier_catalogue("SUP_NOT_FOUND")
        self.assertIsNone(products2)
        self.assertIn("not found", err2.lower())

        self._write_supplier("SUP1", "ACTIVE")
        self._write_product("SKU1", 1, "ACTIVE")

        # link includes an existing product and a missing product -> append vs skip branches
        self.link_repo.add_link("SUP1", "SKU1")
        self.link_repo.add_link("SUP1", "MISSING")

        prods, err3 = self.svc.view_supplier_catalogue("SUP1")
        self.assertIsNone(err3)
        self.assertEqual(1, len(prods))


# =====================================================
# BRANCH TESTS: Service/supplier_service.py (mine)
# Real SupplierRepo (temp file)
# Branches:
# - validate id/name empty
# - create duplicate / success
# - update not found / update with fields / no update when blanks
# - deactivate not found / already inactive / success
# =====================================================
class TestBranch_SupplierService(unittest.TestCase):
    def setUp(self):
        self.suppliers_file = "tmp_suppliers_branch_service.txt"
        _safe_remove(self.suppliers_file)

        self.repo = SupplierRepo(filename=self.suppliers_file)
        self.svc = SupplierService(self.repo)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_create_supplier_branches(self):
        self.assertEqual("Supplier ID cannot be empty", self.svc.create_supplier("", "Name"))
        self.assertEqual("Supplier name cannot be empty", self.svc.create_supplier("SUP1", ""))

        msg1 = self.svc.create_supplier("SUP1", "Supplier One", "07000", "a@b.com")
        self.assertIn("successfully", msg1.lower())

        msg_dup = self.svc.create_supplier("SUP1", "Again", "07000", "x@y.com")
        self.assertIn("already exists", msg_dup.lower())

    def test_update_supplier_branches(self):
        self.assertEqual("Supplier ID cannot be empty", self.svc.update_supplier("", "N"))
        self.assertEqual("Supplier not found", self.svc.update_supplier("MISSING", "N"))

        self.svc.create_supplier("SUP1", "OldName", "111", "old@x.com")

        msg = self.svc.update_supplier("SUP1", " NewName ", " 222 ", " new@x.com ")
        self.assertIn("updated successfully", msg.lower())

        s = self.repo.find_by_id("SUP1")
        self.assertEqual("NewName", s.name)
        self.assertEqual("222", s.phone)
        self.assertEqual("new@x.com", s.email)

        old_name = s.name
        msg2 = self.svc.update_supplier("SUP1", "   ", "   ", "   ")
        self.assertIn("updated successfully", msg2.lower())
        self.assertEqual(old_name, self.repo.find_by_id("SUP1").name)

    def test_deactivate_supplier_branches(self):
        self.assertEqual("Supplier ID cannot be empty", self.svc.deactivate_supplier(""))
        self.assertEqual("Supplier not found", self.svc.deactivate_supplier("MISSING"))

        self.svc.create_supplier("SUP1", "Supplier One", "111", "a@b.com")
        msg = self.svc.deactivate_supplier("SUP1")
        self.assertIn("deactivated successfully", msg.lower())

        msg2 = self.svc.deactivate_supplier("SUP1")
        self.assertIn("already inactive", msg2.lower())


# =====================================================
# BRANCH TESTS: ProductService (shared file)
# I only test the methods I wrote:
# - add_new_product
# - update_product
# - remove_product
# - get_low_stock_products
# - get_dashboard_summary
#
# I use real ProductRepo with a temp products file (and redirect audit log).
# =====================================================
class TestBranch_ProductService_MyMethods(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_branch_productservice.txt"
        self.audit_file = "tmp_audit_branch_productservice.txt"

        _safe_remove(self.products_file)
        _safe_remove(self.audit_file)

        product_service_module.AUDIT_FILE = self.audit_file

        # CategoryRepo is required by constructor in file,
        # but my tested methods do not use it for these paths.
        class CategoryRepoDummy:
            pass

        self.category_repo = CategoryRepoDummy()
        self.product_repo = ProductRepo(filename=self.products_file)
        self.svc = ProductService(self.product_repo, self.category_repo)

    def tearDown(self):
        _safe_remove(self.products_file)
        _safe_remove(self.audit_file)

    def _write_product(self, sku, qty, price=1.0, category="Cat", status="ACTIVE"):
        with open(self.products_file, "a") as f:
            f.write(f"{sku},Name,Desc,{qty},{price},{category},{status}\n")
        self.product_repo.load_products()

    def test_add_new_product_branches(self):
        self.assertEqual("SKU cannot be empty", self.svc.add_new_product("", "N", "D", 1, 1.0))
        self.assertEqual("Name cannot be empty", self.svc.add_new_product("SKU1", "", "D", 1, 1.0))
        self.assertEqual("Quantity must be a whole number", self.svc.add_new_product("SKU1", "N", "D", "abc", 1.0))
        self.assertEqual("Quantity cannot be negative", self.svc.add_new_product("SKU1", "N", "D", -1, 1.0))
        self.assertEqual("Price must be a number", self.svc.add_new_product("SKU1", "N", "D", 1, "xyz"))
        self.assertEqual("Price cannot be negative", self.svc.add_new_product("SKU1", "N", "D", 1, -1.0))

        # duplicate branch
        self._write_product("SKU1", 1, 1.0, "Cat", "ACTIVE")
        self.assertEqual("That SKU already exists", self.svc.add_new_product("SKU1", "N", "D", 1, 1.0))

        # success branch
        msg = self.svc.add_new_product("SKU2", "N2", "D2", 2, 2.5, "Food", user="tf146")
        self.assertIn("successfully", msg.lower())

    def test_update_product_branches(self):
        self.assertEqual("SKU cannot be empty", self.svc.update_product("", "N", "D", 1, 1.0, None))
        self.assertEqual("Product not found", self.svc.update_product("MISSING", "N", "D", 1, 1.0, None))

        self._write_product("SKU1", 1, 1.0, "Cat", "ACTIVE")

        self.assertEqual("Name cannot be empty", self.svc.update_product("SKU1", "", "D", 1, 1.0, None))
        self.assertEqual("Quantity must be a whole number", self.svc.update_product("SKU1", "N", "D", "abc", 1.0, None))
        self.assertEqual("Quantity cannot be negative", self.svc.update_product("SKU1", "N", "D", -1, 1.0, None))
        self.assertEqual("Price must be a number", self.svc.update_product("SKU1", "N", "D", 1, "xyz", None))
        self.assertEqual("Price cannot be negative", self.svc.update_product("SKU1", "N", "D", 1, -1.0, None))

        msg = self.svc.update_product("SKU1", "New", "NewD", 5, 9.99, "Cat", user="tf146")
        self.assertIn("updated successfully", msg.lower())

    def test_remove_product_branches(self):
        self.assertEqual("SKU cannot be empty", self.svc.remove_product("", user="tf146"))
        self.assertEqual("Product not found", self.svc.remove_product("MISSING", user="tf146"))

        self._write_product("SKU1", 1, 1.0, "Cat", "ACTIVE")

        msg = self.svc.remove_product("SKU1", user="tf146")
        self.assertIn("removed successfully", msg.lower())

        # now missing after remove -> not found branch
        self.assertEqual("Product not found", self.svc.remove_product("SKU1", user="tf146"))

    def test_get_low_stock_products_branches(self):
        # invalid threshold branch
        self.assertIsNone(self.svc.get_low_stock_products("abc"))

        # negative threshold branch
        self.assertIsNone(self.svc.get_low_stock_products(-1))

        # valid threshold branch:
        # A -> qty<=threshold (added)
        # B -> bad qty triggers except -> skipped
        # C -> inactive triggers continue -> skipped
        with open(self.products_file, "w") as f:
            f.write("A,Name,Desc,2,1.0,Cat,ACTIVE\n")
            f.write("B,Name,Desc,bad,1.0,Cat,ACTIVE\n")      # NOTE: this will crash ProductRepo.load_products()
            f.write("C,Name,Desc,1,1.0,Cat,INACTIVE\n")
        #
        # IMPORTANT:
        # ProductRepo.load_products() casts int(quantity), so 'bad' would raise ValueError.
        # To keep tests runnable with real repos, I do NOT write invalid ints in file.
        #
        # So instead I test the "inactive continue" branch with INACTIVE,
        # and I test the "qty <= threshold" branch with a valid integer.
        with open(self.products_file, "w") as f:
            f.write("A,Name,Desc,2,1.0,Cat,ACTIVE\n")     # low stock
            f.write("C,Name,Desc,1,1.0,Cat,INACTIVE\n")  # inactive skip

        self.product_repo.load_products()
        low = self.svc.get_low_stock_products(2)
        self.assertEqual(1, len(low))
        self.assertEqual("A", low[0].sku)

    def test_get_dashboard_summary_branches(self):
        # CRITICAL branch (out_of_stock_count > 0)
        with open(self.products_file, "w") as f:
            f.write("A,Name,Desc,0,1.0,Cat,ACTIVE\n")
            f.write("B,Name,Desc,1,1.0,Cat,ACTIVE\n")
            f.write("C,Name,Desc,2,1.0,Cat,ACTIVE\n")
            f.write("D,Name,Desc,3,1.0,Cat,ACTIVE\n")

        self.product_repo.load_products()
        summary = self.svc.get_dashboard_summary(threshold=5)
        self.assertEqual("CRITICAL", summary["system_status"])

        # HEALTHY branch (no out of stock and low_stock_count < 3)
        with open(self.products_file, "w") as f:
            f.write("E,Name,Desc,10,1.0,Cat,ACTIVE\n")
            f.write("F,Name,Desc,9,1.0,Cat,ACTIVE\n")

        self.product_repo.load_products()
        summary2 = self.svc.get_dashboard_summary(threshold=5)
        self.assertEqual("HEALTHY", summary2["system_status"])

        # percent else branch (total_products == 0)
        with open(self.products_file, "w") as f:
            f.write("")
        self.product_repo.load_products()

        summary3 = self.svc.get_dashboard_summary(threshold=5)
        self.assertEqual(0, summary3["low_stock_percent"])
        self.assertEqual(0, summary3["out_of_stock_percent"])

if __name__ == "__main__":
    unittest.main()
