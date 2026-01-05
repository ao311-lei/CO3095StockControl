import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockDecreaseCP(unittest.TestCase):

    def setUp(self):
        self.repo = ProductRepo()
        self.repo.products = []
        self.service = StockService(self.repo)

        product = Product(
            sku="SKU1",
            name="Test Product",
            description="Test description",
            quantity=10,
            price=9.99,
            category="Test Category"
        )

        self.repo.add_product(product)


    # Working input
    def test_valid_stock_decrease(self):
        new_qty = self.service.record_stock_decrease("SKU1", 3)
        self.assertEqual(new_qty, 7)

    # Invalid (no amount)
    def test_zero_amount(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 0)

    # Invalid (negative number on stock decrease)
    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", -5)

    # Invalid SKU
    def test_invalid_sku(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("BADSKU", 1)

    # Invalid (not enough stock)
    def test_insufficient_stock(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 50)


    def test_amount_not_integer(self):
        with self.assertRaises(Exception):
            self.service.record_stock_decrease("SKU1", "2")


    def test_sku_empty_string(self):
            with self.assertRaises(ValueError):
                self.service.record_stock_decrease("   ", 1)

