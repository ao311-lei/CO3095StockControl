import unittest

from Service.stock_history_service import StockHistoryService
from Repo.stock_history_repo import StockHistoryRepo


class TestTimestampedStockHistoryConcolic(unittest.TestCase):
    def setUp(self):
        self.repo = StockHistoryRepo("src/data/stock_history_test.txt")
        self.service = StockHistoryService(self.repo)

    # Working inputs
    def test_concolic_valid_records(self):
        cases = [
            ("SKU1", 5, 15, "increase"),
            ("SKU1", -2, 13, "decrease"),
            ("SKU2", 10, 10, "restock"),
        ]
        for sku, delta, new_qty, action in cases:
            with self.subTest(sku=sku, delta=delta, action=action):
                entry = self.service.record(sku, delta, new_qty, action)
                self.assertEqual(entry.sku, sku)
                self.assertEqual(entry.delta, int(delta))
                self.assertEqual(entry.new_quantity, int(new_qty))

    # Invalid inputs w/ blank sku/action + negative quantity
    def test_concolic_invalid_records(self):
        cases = [
            ("", 1, 1, "increase"),
            ("SKU1", 1, 1, ""),
            ("SKU1", 1, -1, "adjust"),
        ]
        for sku, delta, new_qty, action in cases:
            with self.subTest(sku=sku, action=action, new_qty=new_qty):
                with self.assertRaises(ValueError):
                    self.service.record(sku, delta, new_qty, action)
