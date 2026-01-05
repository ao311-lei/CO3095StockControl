import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockIncreaseBranch(unittest.TestCase):
    def setUp(self):
        self.repo = ProductRepo()
        if hasattr(self.repo, "products"):
            self.repo.products = []
        self.service = StockService(self.repo)

        product = Product(
            sku="SKU1",
            name="Product",
            description="Desc",
            quantity=10,
            price=9.99,
            category="Cat"
        )
        self.repo.add_product(product)

    # Working input
    def test_valid_stock_increase(self):
        new_qty = self.service.record_stock_increase("SKU1", 5)
        self.assertEqual(new_qty, 15)

    # Invalid (negative number on stock increase)
    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_increase("SKU1", -2)
