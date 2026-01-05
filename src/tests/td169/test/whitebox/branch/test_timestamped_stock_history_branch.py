import unittest

from Service.stock_history_service import StockHistoryService
from Repo.stock_history_repo import StockHistoryRepo


class TestTimestampedStockHistoryBranch(unittest.TestCase):
    def setUp(self):
        self.repo = StockHistoryRepo("src/data/stock_history_test.txt")
        self.service = StockHistoryService(self.repo)

    # Working input
    def test_valid_record(self):
        entry = self.service.record("SKU1", -1, 9, "decrease")
        self.assertIsNotNone(entry)

    # Invalid (blank SKU)
    def test_invalid_sku(self):
        with self.assertRaises(ValueError):
            self.service.record("", -1, 9, "decrease")
