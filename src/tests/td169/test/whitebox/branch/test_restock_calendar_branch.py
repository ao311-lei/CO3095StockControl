import unittest

from Service.restock_calendar_service import RestockCalendarService


class _FakeProductRepo:
    def __init__(self):
        self.products = {}

    def add_product(self, sku, qty):
        self.products[sku] = qty

    def find_by_sku(self, sku):
        if sku not in self.products:
            return None
        return type("P", (), {"sku": sku, "quantity": self.products[sku]})

    def get_all_products(self):
        return [type("P", (), {"sku": sku, "quantity": qty}) for sku, qty in self.products.items()]


class TestRestockCalendarBranch(unittest.TestCase):
    def setUp(self):
        self.repo = _FakeProductRepo()
        self.repo.add_product("SKU1", 0)
        self.service = RestockCalendarService(self.repo)

    # Working input (low stock should appear)
    def test_calendar_contains_due_item(self):
        self.service.set_restock_rule("SKU1", 5, 3)
        cal = self.service.get_restock_calendar()
        self.assertTrue(any(item["sku"] == "SKU1" for item in cal))

    # Invalid (rule values)
    def test_invalid_rule_values(self):
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("SKU1", 0, 3)
