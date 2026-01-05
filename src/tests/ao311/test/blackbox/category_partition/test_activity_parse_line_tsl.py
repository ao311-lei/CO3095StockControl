"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: ActivityService._parse_line
TSL spec: specs/activity_parse_line.tsl
Tooling: TSLGenerator (frames in lab) + unittest (execution)
"""

import unittest
from datetime import datetime
from Service.activity_service import ActivityService


class TestActivityParseLineTSL(unittest.TestCase):
    def setUp(self):
        self.svc = ActivityService(filename="unused.txt")

    def test_valid_line(self):
        # Frame: LineFormat=Valid
        line = "2026-01-05 01:00:00 - USER=adora ACTION=LOGIN SUCCESS"
        ts, msg = self.svc._parse_line(line)
        self.assertIsInstance(ts, datetime)
        self.assertEqual(msg, "USER=adora ACTION=LOGIN SUCCESS")

    def test_missing_delimiter(self):
        # Frame: LineFormat=MissingDelimiter [error]
        ts, msg = self.svc._parse_line("2026-01-05 01:00:00 USER=adora ACTION=LOGIN")
        self.assertIsNone(ts)
        self.assertIsNone(msg)

    def test_invalid_timestamp(self):
        # Frame: LineFormat=InvalidTimestamp [error]
        ts, msg = self.svc._parse_line("NOT_A_TIME - USER=adora ACTION=LOGIN")
        self.assertIsNone(ts)
        self.assertIsNone(msg)

    def test_empty_string(self):
        # Frame: LineFormat=EmptyString [error]
        ts, msg = self.svc._parse_line("")
        self.assertIsNone(ts)
        self.assertIsNone(msg)


if __name__ == "__main__":
    unittest.main()
