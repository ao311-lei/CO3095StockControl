import unittest

from Service.stock_history_service import StockHistoryService
from Repo.stock_history_repo import StockHistoryRepo


class TestTimestampedStockHistorySymbolic(unittest.TestCase):
    def setUp(self):
        self.repo = StockHistoryRepo("src/data/stock_history_test.txt")
        self.service = StockHistoryService(self.repo)

    # Working input where sku and action is ok + qty>=0
    def test_path_valid_record(self):
        entry = self.service.record("SKU1", 1, 1, "increase")
        self.assertEqual(entry.sku, "SKU1")

    # Invalid input qty < 0
    def test_path_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.service.record("SKU1", 1, -1, "increase")
