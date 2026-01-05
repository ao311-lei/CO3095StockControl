import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockDecreaseBranch(unittest.TestCase):

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

    def test_amount_positive_branch(self):
        result = self.service.record_stock_decrease("SKU1", 1)
        self.assertEqual(result, 9)

    def test_amount_negative_branch(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", -1)

    def test_stock_sufficient_branch(self):
        result = self.service.record_stock_decrease("SKU1", 2)
        self.assertEqual(result, 8)

    def test_stock_insufficient_branch(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 50)
