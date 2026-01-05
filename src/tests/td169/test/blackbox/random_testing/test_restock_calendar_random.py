import random
import unittest

try:
    from Service.restock_calendar_service import RestockCalendarService
except Exception:
    RestockCalendarService = None


class _FakeProductRepo:
    def __init__(self):
        self.products = {}

    def add(self, sku, qty):
        self.products[sku] = qty

    def find_by_sku(self, sku):
        if sku not in self.products:
            return None
        return type("P", (), {"sku": sku, "quantity": self.products[sku]})

    def get_all_products(self):
        return [
            type("P", (), {"sku": sku, "quantity": qty})
            for sku, qty in self.products.items()
        ]


@unittest.skipIf(RestockCalendarService is None, "RestockCalendarService not importable yet")
class TestRestockCalendarRandom(unittest.TestCase):
    def setUp(self):
        random.seed(202)
        self.repo = _FakeProductRepo()
        self.service = RestockCalendarService(self.repo)

    def test_random_rules_add_and_read(self):
        for i in range(5):
            with self.subTest(i=i):
                sku = f"SKU{random.randint(1, 999)}"
                self.repo.add(sku, random.randint(0, 20))
                reorder_level = random.randint(1, 10)
                lead_days = random.randint(1, 14)

                self.service.set_restock_rule(sku, reorder_level=reorder_level, lead_time_days=lead_days)
                rule = self.service.get_restock_rule(sku)

                self.assertEqual(rule["reorder_level"], reorder_level)
                self.assertEqual(rule["lead_time_days"], lead_days)

    def test_invalid_sku_rejected(self):
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("", reorder_level=5, lead_time_days=3)

    def test_invalid_levels_rejected(self):
        self.repo.add("SKU1", 1)
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("SKU1", reorder_level=0, lead_time_days=3)
        with self.assertRaises(ValueError):
            self.service.set_restock_rule("SKU1", reorder_level=5, lead_time_days=0)

    def test_calendar_contains_due_items(self):
        self.repo.add("SKU1", 0)
        self.service.set_restock_rule("SKU1", reorder_level=5, lead_time_days=3)
        cal = self.service.get_restock_calendar()
        self.assertTrue(any(item["sku"] == "SKU1" for item in cal))
