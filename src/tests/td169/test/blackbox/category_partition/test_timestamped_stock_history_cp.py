import unittest
import re
from pathlib import Path

import Repo.stock_history_repo as stock_history_repo
from Repo.stock_history_repo import StockHistoryRepo
from Service.stock_history_service import StockHistoryService


class TestTimestampedStockHistoryCP(unittest.TestCase):
    def setUp(self):
        stock_history_repo.projectroot = Path(".")
        self.repo = StockHistoryRepo("test_history.txt")
        self.service = StockHistoryService(self.repo)

    def test_valid_record(self):
        entry = self.service.record("SKU1", -2, 8, "DECREASE")
        self.assertIsNotNone(entry)

    def test_invalid_sku(self):
        with self.assertRaises(ValueError):
            self.service.record("", -1, 9, "DECREASE")

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            self.service.record("SKU1", -1, 9, "")

    def test_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.service.record("SKU1", -1, -5, "DECREASE")

    def test_timestamp_format(self):
        entry = self.service.record("SKU2", 5, 15, "INCREASE")
        ts = entry.timestamp if hasattr(entry, "timestamp") else entry.get("timestamp")
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


