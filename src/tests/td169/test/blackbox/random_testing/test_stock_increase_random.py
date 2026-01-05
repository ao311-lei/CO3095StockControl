import unittest
import random

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockIncreaseRandom(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.repo = ProductRepo()
        if hasattr(self.repo, "products"):
            self.repo.products = []

        self.service = StockService(self.repo)

        product = Product(
            sku="SKU1",
            name="Product",
            description="Desc",
            quantity=50,
            price=9.99,
            category="Cat"
        )
        self.repo.add_product(product)

    def test_random_valid_increases(self):
        qty = 50
        for _ in range(20):
            amount = random.randint(1, 10)
            qty += amount
            new_qty = self.service.record_stock_increase("SKU1", amount)
            self.assertEqual(new_qty, qty)

    def test_random_invalid_amounts(self):
        for amount in [0, -1, -5]:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.service.record_stock_increase("SKU1", amount)

    def test_random_invalid_sku(self):
        for _ in range(5):
            with self.assertRaises(ValueError):
                self.service.record_stock_increase("BADSKU", random.randint(1, 5))
