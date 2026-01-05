import random
import unittest

from Service.stock_history_service import StockHistoryService


class _InMemoryHistoryRepo:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)
        return entry

    def get_all(self):
        return list(self.entries)

    def get_by_sku(self, sku):
        return [e for e in self.entries if getattr(e, "sku", None) == sku]


class TestTimestampedStockHistoryRandom(unittest.TestCase):
    def setUp(self):
        random.seed(42)
        self.repo = _InMemoryHistoryRepo()
        self.service = StockHistoryService(self.repo)

    def test_random_valid_records(self):
        for i in range(10):
            with self.subTest(i=i):
                sku = f"SKU{random.randint(1, 999)}"
                delta = random.randint(-50, 50)
                new_qty = random.randint(0, 500)
                action = random.choice(["increase", "decrease", "restock", "adjust"])

                entry = self.service.record(sku, delta, new_qty, action)

                self.assertEqual(entry.sku, sku)
                self.assertEqual(entry.delta, int(delta))
                self.assertEqual(entry.new_quantity, int(new_qty))
                self.assertEqual(entry.action, action)
                self.assertTrue(isinstance(entry.timestamp, str))
                self.assertTrue(len(entry.timestamp) > 0)

    def test_random_invalid_sku_rejected(self):
        bad_skus = [None, "", "   "]
        for s in bad_skus:
            with self.subTest(s=s):
                with self.assertRaises(ValueError):
                    self.service.record(s, 1, 1, "increase")

    def test_random_invalid_action_rejected(self):
        bad_actions = [None, "", "   "]
        for a in bad_actions:
            with self.subTest(a=a):
                with self.assertRaises(ValueError):
                    self.service.record("SKU1", 1, 1, a)

    def test_random_negative_quantity_rejected(self):
        for i in range(5):
            with self.subTest(i=i):
                with self.assertRaises(ValueError):
                    self.service.record("SKU1", random.randint(-10, 10), -1, "adjust")

    def test_history_filtering(self):
        self.service.record("SKU_A", 1, 10, "increase")
        self.service.record("SKU_B", -2, 8, "decrease")
        self.service.record("SKU_A", 3, 13, "increase")

        all_entries = self.service.get_history()
        sku_a_entries = self.service.get_history("SKU_A")

        self.assertEqual(len(all_entries), 3)
        self.assertEqual(len(sku_a_entries), 2)
        self.assertTrue(all(e.sku == "SKU_A" for e in sku_a_entries))
