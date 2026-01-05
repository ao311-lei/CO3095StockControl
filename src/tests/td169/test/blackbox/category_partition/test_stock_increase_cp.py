import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockIncreaseCP(unittest.TestCase):
    def setUp(self):
        self.repo = ProductRepo()
        if hasattr(self.repo, "products"):
            self.repo.products = []
        self.service = StockService(self.repo)

        product = Product(
            sku="SKU1",
            name="Test Product",
            description="Desc",
            quantity=10,
            price=9.99,
            category="TestCategory"
        )
        self.repo.add_product(product)

    def test_valid_increase(self):
        new_qty = self.service.record_stock_increase("SKU1", 5)
        self.assertEqual(new_qty, 15)

    def test_zero_amount(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_increase("SKU1", 0)

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_increase("SKU1", -3)

    def test_invalid_sku(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_increase("SUIIISKU", 1)

    def test_multiple_increases(self):
        self.service.record_stock_increase("SKU1", 2)
        new_qty = self.service.record_stock_increase("SKU1", 3)
        self.assertEqual(new_qty, 15)
