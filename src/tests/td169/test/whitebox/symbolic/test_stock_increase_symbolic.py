import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockIncreaseSymbolic(unittest.TestCase):
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
        self.assertEqual(self.service.record_stock_increase("SKU1", 1), 11)

    # Invalid input where amount<=0
    def test_path_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_increase("SKU1", 0)
