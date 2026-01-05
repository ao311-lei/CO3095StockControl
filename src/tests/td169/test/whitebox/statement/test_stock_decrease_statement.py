import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockDecreaseStatement(unittest.TestCase):

    def setUp(self):
        self.repo = ProductRepo()
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

    def test_amount_less_than_or_is_zero(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 0)

    def test_product_not_found(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("INVALID", 1)

    def test_insufficient_stock(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 20)

    def test_successful_decrease(self):
        product = self.repo.find_by_sku("SKU1")
        product.quantity = 10

        result = self.service.record_stock_decrease("SKU1", 5)
        self.assertEqual(result, 5)

