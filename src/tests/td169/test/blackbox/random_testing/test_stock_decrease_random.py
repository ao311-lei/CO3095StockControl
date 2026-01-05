import unittest
import random

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockDecreaseRandom(unittest.TestCase):
    def setUp(self):
        random.seed(2)
        self.repo = ProductRepo()
        if hasattr(self.repo, "products"):
            self.repo.products = []

        self.service = StockService(self.repo)

        product = Product(
            sku="SKU1",
            name="Product",
            description="Desc",
            quantity=100,
            price=9.99,
            category="Cat"
        )
        self.repo.add_product(product)

    def test_random_valid_decreases(self):
        qty = 100
        for _ in range(20):
            amount = random.randint(1, 5)
            qty -= amount
            new_qty = self.service.record_stock_decrease("SKU1", amount)
            self.assertEqual(new_qty, qty)

    def test_random_invalid_amounts(self):
        for amount in [0, -1, -10]:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.service.record_stock_decrease("SKU1", amount)

    def test_random_excessive_decrease(self):
        with self.assertRaises(ValueError):
            self.service.record_stock_decrease("SKU1", 1000)
