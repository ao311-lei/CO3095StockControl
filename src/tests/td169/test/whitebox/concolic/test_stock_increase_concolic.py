import unittest

from Service.stock_service import StockService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestStockIncreaseConcolic(unittest.TestCase):
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

    # Working inputs
    def test_concolic_valid_increase_cases(self):
        cases = [
            (1, 11),
            (5, 15),
            (10, 20),
        ]
        for amount, expected in cases:
            with self.subTest(amount=amount):
                product = self.repo.find_by_sku("SKU1")
                product.quantity = 10
                new_qty = self.service.record_stock_increase("SKU1", amount)
                self.assertEqual(new_qty, expected)

    # Invalid inputs
    def test_concolic_invalid_increase_cases(self):
        cases = [
            ("SKU1", 0),
            ("SKU1", -1),
            ("BADSKU", 1),
        ]
        for sku, amount in cases:
            with self.subTest(sku=sku, amount=amount):
                with self.assertRaises(ValueError):
                    self.service.record_stock_increase(sku, amount)
