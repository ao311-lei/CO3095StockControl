import unittest
import os

# =========================
# Imports: Models (mine)
# =========================
from model.product import Product
from model.return_item import ReturnItem
from model.supplier import Supplier

# =========================
# Imports: Repos
# =========================
from Repo.return_repo import ReturnRepo
from Repo.supplier_repo import SupplierRepo
from Repo.supplier_product_repo import SupplierProductRepo
from Repo.product_repo import ProductRepo

# =========================
# Imports: Services (mine + shared dependency)
# =========================
from Service.dashboard_chart_service import DashboardChartService
from Service.return_service import ReturnService
from Service.supplier_catalogue_service import SupplierCatalogueService
from Service.supplier_service import SupplierService
from Service.product_service import ProductService

# redirect audit file constants so I do not write into src/data/*
import Service.product_service as product_service_module
import Service.stock_service as stock_service_module
from Service.stock_service import StockService


# =====================================================
# helper: delete file safely
# =====================================================
def _safe_remove(path):
    if os.path.exists(path):
        os.remove(path)


# =====================================================
# Statement White-Box Tests: model/product.py (mine)
# =====================================================
class TestProductModelStatement(unittest.TestCase):
    """
    Statement testing for Product model.
    Goal: execute all statements at least once.
    """

    def test_product_active_and_inactive_statements(self):
        # I execute all assignments in __init__ and the ACTIVE branch in status_text()
        p1 = Product("SKU001", "Test", "Desc", 10, 2.50, "Food", active=True)
        self.assertEqual("ACTIVE", p1.status_text())
        self.assertIn("SKU001", str(p1))  # executes __str__

        # I execute the INACTIVE branch in status_text()
        p2 = Product("SKU002", "Inactive", "Desc", 0, 0.99, "Other", active=False)
        self.assertEqual("INACTIVE", p2.status_text())
        self.assertIn("SKU002", str(p2))


# =====================================================
# Statement White-Box Tests: model/return_item.py (mine)
# =====================================================
class TestReturnItemModelStatement(unittest.TestCase):
    """
    Statement testing for ReturnItem model.
    Goal: execute all assignments in __init__.
    """

    def test_return_item_initialisation(self):
        item = ReturnItem("RET001", "SKU001", 2, "damaged", "REJECTED", "Packaging damaged")
        self.assertEqual("RET001", item.return_id)
        self.assertEqual("SKU001", item.sku)
        self.assertEqual(2, item.quantity)


# =====================================================
# Statement White-Box Tests: model/supplier.py (mine)
# =====================================================
class TestSupplierModelStatement(unittest.TestCase):
    """
    Statement testing for Supplier model.
    Goal: execute __init__ and __str__ with both ACTIVE and INACTIVE.
    """

    def test_supplier_str_statements(self):
        s1 = Supplier("SUP001", "Supplier One", "07123", "s1@example.com", active=True)
        self.assertIn("ACTIVE", str(s1))

        s2 = Supplier("SUP002", "Supplier Two", "07000", "s2@example.com", active=False)
        self.assertIn("INACTIVE", str(s2))


# =====================================================
# Statement White-Box Tests: Repo/return_repo.py (mine)
# =====================================================
class TestReturnRepoStatement(unittest.TestCase):
    """
    Statement testing for ReturnRepo.
    Goal:
    - execute __init__ (file missing path and file exists path)
    - execute save_return() write statements
    """

    def setUp(self):
        self.returns_file = "tmp_returns_statement.txt"
        _safe_remove(self.returns_file)

    def tearDown(self):
        _safe_remove(self.returns_file)

    def test_init_file_missing_creates_file(self):
        # I execute the FileNotFoundError path by starting with no file
        repo = ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_init_file_exists_path(self):
        # I create file first so __init__ executes the try path
        open(self.returns_file, "w").close()
        repo = ReturnRepo(filename=self.returns_file)
        self.assertTrue(os.path.exists(self.returns_file))

    def test_save_return_writes_line(self):
        repo = ReturnRepo(filename=self.returns_file)
        item = ReturnItem("RET100", "SKU100", 1, "good", "ADDED_TO_STOCK", "Approved")
        repo.save_return(item)

        with open(self.returns_file, "r") as f:
            content = f.read()

        self.assertIn("RET100", content)
        self.assertIn("SKU100", content)
        self.assertIn("ADDED_TO_STOCK", content)


# =====================================================
# Statement White-Box Tests: Repo/supplier_repo.py (mine)
# =====================================================
class TestSupplierRepoStatement(unittest.TestCase):
    """
    Statement testing for SupplierRepo.
    Goal: execute load_suppliers, save_suppliers, find_by_id, add_supplier, update_supplier.
    """

    def setUp(self):
        self.suppliers_file = "tmp_suppliers_statement.txt"
        _safe_remove(self.suppliers_file)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_file_missing_path_creates_empty_file(self):
        repo = SupplierRepo(filename=self.suppliers_file)
        self.assertTrue(os.path.exists(self.suppliers_file))
        self.assertEqual([], repo.get_all())

    def test_normal_load_skips_blank_and_defaults(self):
        # I write a file that triggers:
        # - blank line continue
        # - normal parse with full fields
        # - default phone/email/status when short line
        # - INACTIVE status -> active False
        with open(self.suppliers_file, "w") as f:
            f.write("\n")
            f.write("SUP1, Supplier One, 07111, one@x.com, ACTIVE\n")
            f.write("SUP2, Supplier Two\n")
            f.write("SUP3, Supplier Three, 07000, three@x.com, INACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)
        all_sups = repo.get_all()

        self.assertEqual(3, len(all_sups))
        self.assertTrue(repo.find_by_id("SUP1").active)
        self.assertTrue(repo.find_by_id("SUP2").active)   # default ACTIVE
        self.assertFalse(repo.find_by_id("SUP3").active)  # INACTIVE line

    def test_save_suppliers_writes_active_and_inactive(self):
        repo = SupplierRepo(filename=self.suppliers_file)
        repo.suppliers = [
            Supplier("SUP10", "A", "07123", "a@x.com", True),
            Supplier("SUP11", "B", "", "", False),
        ]
        repo.save_suppliers()

        with open(self.suppliers_file, "r") as f:
            content = f.read()

        self.assertIn("SUP10,A,07123,a@x.com,ACTIVE", content)
        self.assertIn("SUP11,B,,,INACTIVE", content)

    def test_update_supplier_true_and_false_paths(self):
        with open(self.suppliers_file, "w") as f:
            f.write("SUP20, Old Name, , , ACTIVE\n")

        repo = SupplierRepo(filename=self.suppliers_file)

        ok = repo.update_supplier(Supplier("SUP20", "New Name", "", "", True))
        self.assertTrue(ok)

        not_ok = repo.update_supplier(Supplier("MISSING", "X", "", "", True))
        self.assertFalse(not_ok)


# =====================================================
# Statement White-Box Tests: Repo/supplier_product_repo.py (mine)
# =====================================================
class TestSupplierProductRepoStatement(unittest.TestCase):
    """
    Statement testing for SupplierProductRepo.
    Goal: execute init, load/save, add_link, remove_link, getters.
    """

    def setUp(self):
        self.links_file = "tmp_supplier_products_statement.txt"
        _safe_remove(self.links_file)

    def tearDown(self):
        _safe_remove(self.links_file)

    def test_init_creates_file(self):
        repo = SupplierProductRepo(filename=self.links_file)
        self.assertTrue(os.path.exists(self.links_file))

    def test_load_save_add_remove_and_getters(self):
        repo = SupplierProductRepo(filename=self.links_file)

        # save_all_links statements
        repo.save_all_links([("SUP1", "SKU1"), ("SUP2", "SKU2")])
        self.assertEqual([("SUP1", "SKU1"), ("SUP2", "SKU2")], repo.load_all_links())

        # add_link True then False (duplicate)
        self.assertTrue(repo.add_link("SUP3", "SKU3"))
        self.assertFalse(repo.add_link("SUP3", "SKU3"))

        # remove_link True then False
        self.assertTrue(repo.remove_link("SUP1", "SKU1"))
        self.assertFalse(repo.remove_link("MISSING", "MISSING"))

        # getter statements
        repo.save_all_links([("SUP9", "SKU9"), ("SUP9", "SKU10"), ("SUP10", "SKU9")])
        self.assertEqual(["SKU9", "SKU10"], repo.get_products_for_supplier("SUP9"))
        self.assertEqual(["SUP9", "SUP10"], repo.get_suppliers_for_product("SKU9"))


# =====================================================
# Statement White-Box Tests: Service/dashboard_chart_service.py (mine)
# Real ProductRepo + temp file (no dummy repo)
# =====================================================
class TestDashboardChartServiceStatement(unittest.TestCase):
    """
    Statement testing for DashboardChartService.
    Goal: execute methods and produce output lines.
    """

    def setUp(self):
        self.products_file = "tmp_products_statement_dashboard.txt"
        _safe_remove(self.products_file)
        self.product_repo = ProductRepo(filename=self.products_file)
        self.svc = DashboardChartService(self.product_repo)

    def tearDown(self):
        _safe_remove(self.products_file)

    def test_empty_products_statements(self):
        lines = self.svc.build_dashboard_chart_lines(threshold=5)
        joined = "\n".join(lines)
        self.assertIn("[ DASHBOARD CHARTS ]", joined)
        self.assertIn("(No categories found)", joined)

    def test_non_empty_products_statements(self):
        # I write valid product rows (quantity must be int for ProductRepo.load_products)
        with open(self.products_file, "w") as f:
            f.write("A,ProdA,Desc,0,1.0,,ACTIVE\n")
            f.write("B,ProdB,Desc,3,1.0,Food,ACTIVE\n")
            f.write("C,ProdC,Desc,10,1.0,Food,ACTIVE\n")
            f.write("D,ProdD,Desc,25,1.0,Drinks,ACTIVE\n")
            f.write("E,ProdE,Desc,5,1.0,Cat,INACTIVE\n")  # inactive skip statements

        self.product_repo.load_products()

        status = self.svc.get_inventory_status_counts(threshold=5)
        self.assertTrue("in_stock" in status)

        buckets = self.svc.get_stock_bucket_counts()
        self.assertTrue("21+" in buckets)

        counts = self.svc.get_category_counts()
        self.assertTrue("Food" in counts)

        lines = self.svc.build_dashboard_chart_lines(threshold=5)
        self.assertTrue(len(lines) > 0)


# =====================================================
# Statement White-Box Tests: Service/return_service.py (mine)
# Real ProductRepo + ReturnRepo + real StockService (dependency), all temp files
# =====================================================
class TestReturnServiceStatement(unittest.TestCase):
    """
    Statement testing for ReturnService.process_return using real repos/temp files.
    Goal: hit multiple early returns + record outcomes.
    """

    def setUp(self):
        self.products_file = "tmp_products_statement_return.txt"
        self.returns_file = "tmp_returns_statement_return.txt"
        self.audit_file = "tmp_audit_statement_stock.txt"

        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

        # redirect StockService audit path to temp
        stock_service_module.AUDIT_FILE = self.audit_file

        self.product_repo = ProductRepo(filename=self.products_file)
        self.return_repo = ReturnRepo(filename=self.returns_file)
        self.stock_service = StockService(self.product_repo)
        self.svc = ReturnService(self.product_repo, self.stock_service, self.return_repo)

    def tearDown(self):
        _safe_remove(self.products_file)
        _safe_remove(self.returns_file)
        _safe_remove(self.audit_file)

    def _write_product(self, sku, qty, status="ACTIVE"):
        with open(self.products_file, "a") as f:
            f.write(f"{sku},Name,Desc,{qty},1.0,Cat,{status}\n")
        self.product_repo.load_products()

    def test_multiple_paths_statements(self):
        # sku empty early return
        self.assertEqual("SKU cannot be empty", self.svc.process_return("", 1, "sealed"))

        # product not found (records rejection)
        msg = self.svc.process_return("MISSING", 1, "sealed")
        self.assertIn("Product not found", msg)

        # inactive product
        self._write_product("SKU1", 5, status="INACTIVE")
        msg2 = self.svc.process_return("SKU1", 1, "sealed")
        self.assertIn("inactive", msg2.lower())

        # quantity not int
        self._write_product("SKU2", 5, status="ACTIVE")
        self.assertEqual("Quantity must be a whole number", self.svc.process_return("SKU2", "abc", "sealed"))

        # qty <= 0
        self.assertEqual("Quantity must be greater than 0", self.svc.process_return("SKU2", 0, "sealed"))

        # condition not accepted (records rejection but no stock increase)
        msg3 = self.svc.process_return("SKU2", 1, "damaged")
        self.assertIn("NOT added to stock", msg3)

        # accepted condition -> stock increase success
        msg4 = self.svc.process_return("SKU2", 2, "sealed")
        self.assertIn("Return accepted", msg4)


# =====================================================
# Statement White-Box Tests: Service/supplier_catalogue_service.py (mine)
# Real repos/temp files
# =====================================================
class TestSupplierCatalogueServiceStatement(unittest.TestCase):
    """
    Statement testing for SupplierCatalogueService with real repos.
    """

    def setUp(self):
        self.suppliers_file = "tmp_suppliers_statement_catalogue.txt"
        self.links_file = "tmp_links_statement_catalogue.txt"
        self.products_file = "tmp_products_statement_catalogue.txt"

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

    def test_statements_across_methods(self):
        # empty inputs
        self.assertIn("cannot be empty", self.svc.link_product_to_supplier("", "SKU1").lower())

        # supplier not found
        self._write_product("SKU1", 1, "ACTIVE")
        self.assertEqual("Supplier not found.", self.svc.link_product_to_supplier("SUP1", "SKU1"))

        # supplier inactive
        self._write_supplier("SUP1", "INACTIVE")
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP1", "SKU1").lower())

        # product not found
        self._write_supplier("SUP2", "ACTIVE")
        self.assertEqual("Product not found.", self.svc.link_product_to_supplier("SUP2", "MISSING"))

        # product inactive
        self._write_product("SKU2", 1, "INACTIVE")
        self.assertIn("inactive", self.svc.link_product_to_supplier("SUP2", "SKU2").lower())

        # success link then duplicate
        self._write_product("SKU3", 1, "ACTIVE")
        msg1 = self.svc.link_product_to_supplier("SUP2", "SKU3")
        self.assertIn("successfully", msg1.lower())

        msg2 = self.svc.link_product_to_supplier("SUP2", "SKU3")
        self.assertIn("already", msg2.lower())

        # unlink success and unlink missing
        self.assertIn("removed", self.svc.unlink_product_from_supplier("SUP2", "SKU3").lower())
        self.assertIn("does not exist", self.svc.unlink_product_from_supplier("SUP2", "SKU3").lower())

        # view supplier catalogue
        prods, err = self.svc.view_supplier_catalogue("SUP2")
        self.assertIsNone(err)
        self.assertTrue(isinstance(prods, list))


# =====================================================
# Statement White-Box Tests: Service/supplier_service.py (mine)
# Real SupplierRepo/temp file
# =====================================================
class TestSupplierServiceStatement(unittest.TestCase):
    """
    Statement testing for SupplierService using real repo.
    """

    def setUp(self):
        self.suppliers_file = "tmp_suppliers_statement_service.txt"
        _safe_remove(self.suppliers_file)

        self.repo = SupplierRepo(filename=self.suppliers_file)
        self.svc = SupplierService(self.repo)

    def tearDown(self):
        _safe_remove(self.suppliers_file)

    def test_statements_across_methods(self):
        # create invalid id/name
        self.assertEqual("Supplier ID cannot be empty", self.svc.create_supplier("", "Name"))
        self.assertEqual("Supplier name cannot be empty", self.svc.create_supplier("SUP1", ""))

        # create success
        msg = self.svc.create_supplier("SUP1", "Supplier One", "07123", "a@b.com")
        self.assertIn("successfully", msg.lower())

        # duplicate
        msg2 = self.svc.create_supplier("SUP1", "Again")
        self.assertIn("already exists", msg2.lower())

        # update not found
        self.assertEqual("Supplier not found", self.svc.update_supplier("MISSING", "X"))

        # update success
        msg3 = self.svc.update_supplier("SUP1", " NewName ", " 07000 ", " new@x.com ")
        self.assertIn("updated successfully", msg3.lower())

        # deactivate success then already inactive
        msg4 = self.svc.deactivate_supplier("SUP1")
        self.assertIn("deactivated successfully", msg4.lower())

        msg5 = self.svc.deactivate_supplier("SUP1")
        self.assertIn("already inactive", msg5.lower())

        # list
        all_sups = self.svc.list_suppliers()
        self.assertTrue(len(all_sups) >= 1)


# =====================================================
# Statement White-Box Tests: ProductRepo (shared file)
# I only test the methods I claimed.
# Real repo/temp file
# =====================================================
class TestProductRepoStatement(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_statement_repo.txt"
        _safe_remove(self.products_file)

    def tearDown(self):
        _safe_remove(self.products_file)

    def test_init_add_remove_update_get_all_statements(self):
        repo = ProductRepo(filename=self.products_file)

        # add_product statements
        p = Product("SKU100", "Name", "Desc", 5, 1.99, "Food", True)
        repo.add_product(p)
        self.assertEqual(1, len(repo.get_all_products()))

        # remove true / false statements
        self.assertTrue(repo.remove_by_sku("SKU100"))
        self.assertFalse(repo.remove_by_sku("MISSING"))

        # update false statements (product missing)
        self.assertFalse(repo.update_product("MISSING", "N", "D", 1, 1.0, "C"))


# =====================================================
# Statement White-Box Tests: ProductService (shared file)
# Only methods I claimed:
# add_new_product, update_product, remove_product, get_low_stock_products, get_dashboard_summary
#
# Real ProductRepo/temp products file
# Redirect AUDIT_FILE to temp
# =====================================================
class TestProductServiceStatement(unittest.TestCase):
    def setUp(self):
        self.products_file = "tmp_products_statement_productservice.txt"
        self.audit_file = "tmp_audit_statement_productservice.txt"

        _safe_remove(self.products_file)
        _safe_remove(self.audit_file)

        product_service_module.AUDIT_FILE = self.audit_file

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

    def test_add_update_remove_and_reports_statements(self):
        # add early returns
        self.assertEqual("SKU cannot be empty", self.svc.add_new_product("", "N", "D", 1, 1.0))
        self.assertEqual("Name cannot be empty", self.svc.add_new_product("SKU1", "", "D", 1, 1.0))
        self.assertEqual("Quantity must be a whole number", self.svc.add_new_product("SKU1", "N", "D", "abc", 1.0))
        self.assertEqual("Quantity cannot be negative", self.svc.add_new_product("SKU1", "N", "D", -1, 1.0))
        self.assertEqual("Price must be a number", self.svc.add_new_product("SKU1", "N", "D", 1, "xyz"))
        self.assertEqual("Price cannot be negative", self.svc.add_new_product("SKU1", "N", "D", 1, -1.0))

        # add success + duplicate
        msg = self.svc.add_new_product("SKU1", "Name", "Desc", 1, 1.0, "Food", user="tf146")
        self.assertIn("successfully", msg.lower())
        self.assertEqual("That SKU already exists", self.svc.add_new_product("SKU1", "Name", "Desc", 1, 1.0))

        # update paths
        self.assertEqual("SKU cannot be empty", self.svc.update_product("", "N", "D", 1, 1.0, None))
        self.assertEqual("Product not found", self.svc.update_product("MISSING", "N", "D", 1, 1.0, None))
        self.assertEqual("Name cannot be empty", self.svc.update_product("SKU1", "", "D", 1, 1.0, None))

        ok = self.svc.update_product("SKU1", "New", "NewD", 5, 9.99, "Cat", user="tf146")
        self.assertIn("updated successfully", ok.lower())

        # remove paths
        self.assertEqual("SKU cannot be empty", self.svc.remove_product("", user="tf146"))
        self.assertEqual("Product not found", self.svc.remove_product("MISSING", user="tf146"))

        ok2 = self.svc.remove_product("SKU1", user="tf146")
        self.assertIn("removed successfully", ok2.lower())

        # low stock / dashboard summary statements
        self._write_product("A", 0, 1.0, "Cat", "ACTIVE")
        self._write_product("B", 2, 1.0, "Cat", "ACTIVE")
        summary = self.svc.get_dashboard_summary(threshold=5)
        self.assertTrue("system_status" in summary)

        low = self.svc.get_low_stock_products(5)
        self.assertTrue(isinstance(low, list))

if __name__ == "__main__":
    unittest.main()
