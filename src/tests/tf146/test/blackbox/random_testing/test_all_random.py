"""
Black-box testing using RANDOM testing (single-file, REAL repos + REAL temp files).


- Uses TEMP files so I do not touch src/data/*
- Uses a fixed rand seed so results are repeatable
- Checks external behaviour (messages, file persistence, quantity changes) not internals

"""

import os
import random
import tempfile
import unittest

# -------------------------
# Imports from project
# -------------------------
from model.product import Product
from model.supplier import Supplier

from Repo.product_repo import ProductRepo
from Repo.supplier_repo import SupplierRepo
from Repo.supplier_product_repo import SupplierProductRepo
from Repo.return_repo import ReturnRepo
from Repo.category_repo import CategoryRepo

from Service.dashboard_chart_service import DashboardChartService
from Service.supplier_service import SupplierService
from Service.supplier_catalogue_service import SupplierCatalogueService
from Service.return_service import ReturnService
from Service.product_service import ProductService

# Use real StockService (written by teammate, but required by ReturnService)
from Service.stock_service import StockService

# Redirect audit constants safely to temp files (so tests don't require src/data/audit_log.txt)
import Service.product_service as product_service_module
import Service.stock_service as stock_service_module


# ------------------------------------------------------------
# Helpers for writing repo files in the correct formats
# ------------------------------------------------------------
def write_products_file(path, products):
    """
    ProductRepo format per line:
      sku,name,description,quantity,price,category,status
    status is ACTIVE or INACTIVE
    """
    with open(path, "w", encoding="utf-8") as f:
        for p in products:
            category = p.category if p.category is not None else ""
            status = "ACTIVE" if getattr(p, "active", True) else "INACTIVE"
            f.write(f"{p.sku},{p.name},{p.description},{p.quantity},{p.price},{category},{status}\n")


def write_suppliers_file(path, suppliers):
    """
    SupplierRepo format per line:
      supplier_id,name,phone,email,status
    status is ACTIVE or INACTIVE
    """
    with open(path, "w", encoding="utf-8") as f:
        for s in suppliers:
            status = "ACTIVE" if s.active else "INACTIVE"
            f.write(f"{s.supplier_id},{s.name},{s.phone},{s.email},{status}\n")


def seed_categories_file_minimal(path):
    """
    CategoryRepo signature requires filename. The exact format can vary between teams.
    For these tests, ProductService methods I'm testing do not rely on categories,
    so I only need the file to exist (and optionally have a few simple lines).
    """
    with open(path, "w", encoding="utf-8") as f:
        # keep it simple & harmless
        f.write("Food\n")
        f.write("Tech\n")
        f.write("Home\n")


# ============================================================
# RANDOM BLACK-BOX TESTS (REAL repos + REAL temp files)
# ============================================================
class TestBB_Random_All_RealRepos(unittest.TestCase):
    """
    Random testing with a fixed seed for repeatability.
    All repo files are created inside a temp folder.
    """

    def setUp(self):
        random.seed(146)  # repeatable on lab machines

        # Temp directory so no real project data is touched
        self.tmpdir = tempfile.TemporaryDirectory()
        base = self.tmpdir.name

        # Temp data files
        self.products_path = os.path.join(base, "products.txt")
        self.suppliers_path = os.path.join(base, "suppliers.txt")
        self.links_path = os.path.join(base, "supplier_products.txt")
        self.returns_path = os.path.join(base, "returns.txt")
        self.categories_path = os.path.join(base, "categories.txt")
        self.audit_path = os.path.join(base, "audit_log.txt")

        # Ensure audit file exists (and redirect modules to it)
        open(self.audit_path, "a", encoding="utf-8").close()
        product_service_module.AUDIT_FILE = self.audit_path
        stock_service_module.AUDIT_FILE = self.audit_path

        # Seed categories (CategoryRepo requires filename)
        seed_categories_file_minimal(self.categories_path)

        # --------------------------------------------------------
        # Create random_testing but sensible product & supplier sets
        # --------------------------------------------------------
        categories = ["Food", "Tech", "Home", None, "   "]
        products = []
        for i in range(20):
            sku = f"SKU{i:02d}"
            name = f"Product{i}"
            desc = "desc"
            qty = random.randint(0, 30)
            price = round(random.uniform(0.0, 50.0), 2)
            cat = random.choice(categories)
            active = random.choice([True, True, True, False])  # mostly active
            products.append(Product(sku, name, desc, qty, price, cat, active=active))
        write_products_file(self.products_path, products)

        suppliers = []
        for i in range(6):
            supplier_id = f"SUP{i}"
            name = f"Supplier{i}"
            active = random.choice([True, True, False])
            suppliers.append(Supplier(supplier_id, name, phone="", email="", active=active))
        write_suppliers_file(self.suppliers_path, suppliers)

        # --------------------------------------------------------
        # Real repos (temp-file backed)
        # --------------------------------------------------------
        self.product_repo = ProductRepo(filename=self.products_path)
        self.supplier_repo = SupplierRepo(filename=self.suppliers_path)
        self.link_repo = SupplierProductRepo(filename=self.links_path)
        self.return_repo = ReturnRepo(filename=self.returns_path)
        self.category_repo = CategoryRepo(filename=self.categories_path)

        # --------------------------------------------------------
        # Real services
        # --------------------------------------------------------
        self.chart_service = DashboardChartService(self.product_repo)
        self.supplier_service = SupplierService(self.supplier_repo)
        self.catalogue_service = SupplierCatalogueService(
            self.supplier_repo, self.product_repo, self.link_repo
        )

        self.stock_service = StockService(self.product_repo)
        self.return_service = ReturnService(self.product_repo, self.stock_service, self.return_repo)

        # ProductService (include ONLY the methods I claimed)
        self.product_service = ProductService(self.product_repo, self.category_repo)

    def tearDown(self):
        # Close temp dir properly (prevents ResourceWarning)
        self.tmpdir.cleanup()

    # ============================================================
    # DashboardChartService (random_testing checks)
    # ============================================================
    def test_random_dashboard_inventory_counts_sum_to_active(self):
        threshold = random.randint(0, 10)
        counts = self.chart_service.get_inventory_status_counts(threshold)

        active_products = [p for p in self.product_repo.get_all_products() if getattr(p, "active", True) is True]
        self.assertEqual(
            counts["in_stock"] + counts["low_stock"] + counts["out_of_stock"],
            len(active_products)
        )

    def test_random_dashboard_category_counts_sum_to_active(self):
        counts = self.chart_service.get_category_counts()
        total = sum(counts.values())

        active_products = [p for p in self.product_repo.get_all_products() if getattr(p, "active", True) is True]
        self.assertEqual(total, len(active_products))

    def test_random_dashboard_build_lines_contains_headers(self):
        threshold = random.randint(0, 10)
        lines = self.chart_service.build_dashboard_chart_lines(threshold)
        joined = "\n".join(lines)

        self.assertIn("[ DASHBOARD CHARTS ]", joined)
        self.assertIn("--- Inventory Status ---", joined)
        self.assertIn("--- Stock Level Buckets ---", joined)
        self.assertIn("--- Product Categories (Top 5) ---", joined)

    # ============================================================
    # SupplierCatalogueService + SupplierProductRepo (random_testing link/unlink)
    # ============================================================
    def test_random_linking_active_supplier_and_product(self):
        active_suppliers = [s for s in self.supplier_repo.get_all() if s.active]
        active_products = [p for p in self.product_repo.get_all_products() if getattr(p, "active", True)]

        if not active_suppliers or not active_products:
            self.skipTest("Not enough active suppliers/products for link test")

        supplier = random.choice(active_suppliers)
        chosen_products = random.sample(active_products, min(5, len(active_products)))

        for p in chosen_products:
            msg = self.catalogue_service.link_product_to_supplier(supplier.supplier_id, p.sku)
            # Could be first link or duplicate if random_testing repeats
            self.assertIn(
                msg,
                ["Product linked to supplier successfully.", "This supplier is already linked to that product."]
            )

        # External check: repo contains at least some of those SKUs
        repo_skus = self.link_repo.get_products_for_supplier(supplier.supplier_id)
        self.assertTrue(len(repo_skus) > 0)

    def test_random_unlink_removes_link(self):
        active_suppliers = [s for s in self.supplier_repo.get_all() if s.active]
        active_products = [p for p in self.product_repo.get_all_products() if getattr(p, "active", True)]

        if not active_suppliers or not active_products:
            self.skipTest("Not enough active suppliers/products for unlink test")

        s = random.choice(active_suppliers)
        p = random.choice(active_products)

        # Ensure link exists
        self.catalogue_service.link_product_to_supplier(s.supplier_id, p.sku)

        # Now unlink and confirm removed
        msg = self.catalogue_service.unlink_product_from_supplier(s.supplier_id, p.sku)
        self.assertEqual("Link removed successfully.", msg)

        skus_after = self.link_repo.get_products_for_supplier(s.supplier_id)
        self.assertNotIn(p.sku, skus_after)

    # ============================================================
    # SupplierService (random_testing create/update)
    # ============================================================
    def test_random_create_supplier_unique_ids(self):
        for _ in range(5):
            sid = f"SUP_NEW_{random.randint(1000, 9999)}"
            name = f"Name{random.randint(1, 999)}"

            msg = self.supplier_service.create_supplier(sid, name)
            self.assertEqual("Supplier created successfully", msg)

            self.assertIsNotNone(self.supplier_repo.find_by_id(sid))

    def test_random_update_supplier_changes_fields(self):
        suppliers = self.supplier_repo.get_all()
        if not suppliers:
            self.skipTest("No suppliers to update")

        s = random.choice(suppliers)

        new_name = f"Updated{random.randint(1, 999)}"
        new_phone = str(random.randint(10000, 99999))
        new_email = f"u{random.randint(1, 999)}@x.com"

        msg = self.supplier_service.update_supplier(s.supplier_id, new_name, phone=new_phone, email=new_email)
        self.assertEqual("Supplier updated successfully", msg)

        updated = self.supplier_repo.find_by_id(s.supplier_id)
        self.assertEqual(updated.name, new_name)
        self.assertEqual(updated.phone, new_phone)
        self.assertEqual(updated.email, new_email)

    # ============================================================
    # ReturnService (random_testing accepted vs rejected condition)
    # ============================================================
    def test_random_return_success_increases_quantity(self):
        accepted_conditions = ["sealed", "unopened", "resellable"]

        active_products = [p for p in self.product_repo.get_all_products() if getattr(p, "active", True)]
        if not active_products:
            self.skipTest("No active products for return test")

        p = random.choice(active_products)
        old_qty = int(p.quantity)

        qty = random.randint(1, 5)
        condition = random.choice(accepted_conditions)

        msg = self.return_service.process_return(p.sku, qty, condition)
        self.assertIn("Return accepted. Stock updated. New quantity:", msg)

        updated = self.product_repo.find_by_sku(p.sku)
        self.assertEqual(int(updated.quantity), old_qty + qty)

    def test_random_return_rejected_condition_does_not_change_stock(self):
        bad_conditions = ["damaged", "opened", "broken", "used"]

        active_products = [p for p in self.product_repo.get_all_products() if getattr(p, "active", True)]
        if not active_products:
            self.skipTest("No active products for rejected return test")

        p = random.choice(active_products)
        old_qty = int(p.quantity)

        qty = random.randint(1, 5)
        condition = random.choice(bad_conditions)

        msg = self.return_service.process_return(p.sku, qty, condition)
        self.assertEqual("Return recorded but NOT added to stock (condition not accepted).", msg)

        updated = self.product_repo.find_by_sku(p.sku)
        self.assertEqual(int(updated.quantity), old_qty)

    # ============================================================
    # ProductRepo (methods I claimed) - simple random_testing checks
    # ============================================================
    def test_random_product_repo_remove_by_sku_true_or_false(self):
        products = self.product_repo.get_all_products()
        if not products:
            self.skipTest("No products to remove")

        # 50/50 chance: existing sku or missing sku
        if random.choice([True, False]):
            sku = random.choice(products).sku
            removed = self.product_repo.remove_by_sku(sku)
            self.assertTrue(removed)
        else:
            removed = self.product_repo.remove_by_sku("MISSING_SKU_XXX")
            self.assertFalse(removed)

    def test_random_product_repo_update_product_existing_or_missing(self):
        products = self.product_repo.get_all_products()
        if not products:
            self.skipTest("No products to update")

        if random.choice([True, False]):
            p = random.choice(products)
            ok = self.product_repo.update_product(
                p.sku, "NewName", "NewDesc", int(p.quantity), float(p.price), p.category
            )
            self.assertTrue(ok)
        else:
            ok = self.product_repo.update_product(
                "MISSING_SKU_YYY", "N", "D", 1, 1.0, None
            )
            self.assertFalse(ok)

    # ============================================================
    # ProductService (ONLY methods I claimed) - random_testing checks
    # ============================================================
    def test_random_product_service_add_update_remove_happy_path(self):
        # Add a brand new sku (avoid collisions)
        sku = f"NEW_{random.randint(10000, 99999)}"
        name = "RandProd"
        desc = "desc"
        qty = random.randint(0, 10)
        price = round(random.uniform(0.0, 20.0), 2)
        cat = random.choice(["Food", "Tech", None])

        msg_add = self.product_service.add_new_product(sku, name, desc, qty, price, cat, user="tf146")
        self.assertEqual("Product added successfully", msg_add)

        # Update it
        msg_up = self.product_service.update_product(sku, "RandProd2", "desc2", qty + 1, price + 1.0, cat, user="tf146")
        self.assertEqual("Product updated successfully", msg_up)

        # Remove it
        msg_rm = self.product_service.remove_product(sku, user="tf146")
        self.assertEqual("Product removed successfully", msg_rm)

    def test_random_product_service_get_low_stock_products(self):
        # Random threshold (valid)
        threshold = random.randint(0, 10)
        low = self.product_service.get_low_stock_products(threshold)

        # External behaviour: when threshold is valid (>=0 int), should return a list (possibly empty)
        self.assertIsInstance(low, list)

    def test_random_product_service_get_dashboard_summary_returns_keys(self):
        summary = self.product_service.get_dashboard_summary(threshold=random.randint(0, 10))
        # Check required keys exist (external contract)
        for key in ["total_products", "total_units", "low_stock_count", "out_of_stock_count", "system_status"]:
            self.assertIn(key, summary)

if __name__ == "__main__":
    unittest.main()
