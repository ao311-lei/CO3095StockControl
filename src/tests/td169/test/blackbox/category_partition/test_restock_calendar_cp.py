import unittest

from Service.restock_calendar_service import RestockCalendarService
from Repo.product_repo import ProductRepo

class TestRestockCalendarCP(unittest.TestCase):
    def setUp(self):
        self.repo = ProductRepo()
        self.service = RestockCalendarService(self.repo)

    def test_valid_rule(self):
        self.service.set_restock_rule("SKU1", 5, 7)

    def test_overwrite_rule(self):
        self.service.set_restock_rule("SKU1", 5, 7)
        self.service.set_restock_rule("SKU1", 10, 3)

    def test_invalid_sku(self):
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("", 5, 7)

    def test_negative_reorder_level(self):
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("SKU1", -1, 7)
