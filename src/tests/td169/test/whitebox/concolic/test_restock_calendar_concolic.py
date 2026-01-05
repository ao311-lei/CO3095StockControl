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


class TestRestockCalendarConcolic(unittest.TestCase):
    def setUp(self):
        self.repo = _FakeProductRepo()
        self.service = RestockCalendarService(self.repo)

    # Working inputs
    def test_concolic_due_items(self):
        self.repo.add_product("SKU1", 0)
        self.repo.add_product("SKU2", 10)

        self.service.set_restock_rule("SKU1", 5, 3)
        self.service.set_restock_rule("SKU2", 5, 3)

        cal = self.service.get_restock_calendar()
        self.assertTrue(any(item["sku"] == "SKU1" for item in cal))
        self.assertFalse(any(item["sku"] == "SKU2" for item in cal))

    # Invalid
    def test_concolic_invalid_rules(self):
        cases = [
            ("", 5, 3),
            ("SKU1", 0, 3),
            ("SKU1", 5, 0),
        ]
        self.repo.add_product("SKU1", 1)

        for sku, level, days in cases:
            with self.subTest(sku=sku, level=level, days=days):
                with self.assertRaises(ValueError):
                    self.service.set_restock_rule(sku, level, days)
