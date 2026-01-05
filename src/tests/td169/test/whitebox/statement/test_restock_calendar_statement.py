import unittest
from Service.restock_calendar_service import RestockCalendarService
from Repo.product_repo import ProductRepo
from model.product import Product


class TestRestockCalendarStatement(unittest.TestCase):
    def setUp(self):
        self.repo = ProductRepo()
        if hasattr(self.repo, "products"):
            self.repo.products = []

        product = Product(
            sku="SKU1",
            name="Product",
            description="Desc",
            quantity=2,
            price=9.99,
            category="Cat"
        )
        self.repo.add_product(product)

        self.service = RestockCalendarService(self.repo)

    # Valid restock rule
    def test_set_restock_rule(self):
        rule = self.service.set_restock_rule("SKU1", 5, 3)
        self.assertEqual(rule["reorder_level"], 5)

    # Calendar generated
    def test_get_restock_calendar(self):
        self.service.set_restock_rule("SKU1", 5, 3)
        cal = self.service.get_restock_calendar()
        self.assertEqual(len(cal), 1)

    # Invalid SKU
    def test_invalid_sku(self):
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("", 5, 3)
