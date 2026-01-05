import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockDecreaseConcolic(unittest.TestCase):
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

    def test_concolic_valid_decrease_cases(self):
        cases = [
            (1, 9),
            (3, 7),
            (5, 5),
        ]
        for amount, expected in cases:
            with self.subTest(amount=amount):
                product = self.repo.find_by_sku("SKU1")
                product.quantity = 10
                new_qty = self.service.record_stock_decrease("SKU1", amount)
                self.assertEqual(new_qty, expected)

    def test_concolic_invalid_decrease_cases(self):
        cases = [
            0,
            -1,
            50,
        ]
        for amount in cases:
            with self.subTest(amount=amount):
                product = self.repo.find_by_sku("SKU1")
                product.quantity = 10
                with self.assertRaises(ValueError):
                    self.service.record_stock_decrease("SKU1", amount)
