import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockDecreaseSymbolic(unittest.TestCase):
    def setUp(self):
        self.repo = ProductRepo()
        if hasattr(self.repo, "products"):
            self.repo.products = []
        self.service = StockService(self.repo)

        self.repo.add_product(Product("SKU1", "P", "D", 10, 9.99, "C"))

    # Working input
    def test_path_success(self):
        product = self.repo.find_by_sku("SKU1")
        product.quantity = 10
        self.assertEqual(self.service.record_stock_decrease("SKU1", 10), 0)

    # Invalid input where stock<amount
    def test_path_insufficient_stock(self):
        product = self.repo.find_by_sku("SKU1")
        product.quantity = 3
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 4)
