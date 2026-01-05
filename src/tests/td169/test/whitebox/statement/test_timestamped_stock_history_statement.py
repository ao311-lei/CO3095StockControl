import unittest
from Service.stock_history_service import StockHistoryService
from Repo.stock_history_repo import StockHistoryRepo


class TestTimestampedStockHistoryStatement(unittest.TestCase):

    # Valid record
    def test_valid_record(self):
        repo = StockHistoryRepo("test.txt")
        service = StockHistoryService(repo)
        entry = service.record("SKU1", 5, 10, "increase")
        self.assertEqual(entry.sku, "SKU1")

    # Invalid SKU
    def test_invalid_sku(self):
        repo = StockHistoryRepo("test.txt")
        service = StockHistoryService(repo)
        with self.assertRaises(ValueError):
            service.record("", 5, 10, "increase")

    # Invalid quantity
    def test_invalid_quantity(self):
        repo = StockHistoryRepo("test.txt")
        service = StockHistoryService(repo)
        with self.assertRaises(ValueError):
            service.record("SKU1", 5, -1, "increase")
