"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: PurchaseOrderService.validate_date
TSL spec: specs/po_validate_date.tsl
Tooling: TSLGenerator (frames in lab) + unittest (execution)
"""

import unittest
from datetime import date, timedelta
from Service.purchase_order_service import PurchaseOrderService


class TestPOValidateDateTSL(unittest.TestCase):
    def setUp(self):
        self.svc = PurchaseOrderService()

    def test_valid_future(self):
        # Frame: ValidFuture
        future = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertTrue(self.svc.validate_date(future))

    def test_today(self):
        # Frame: Today
        today = date.today().strftime("%Y-%m-%d")
        self.assertTrue(self.svc.validate_date(today))

    def test_past_date(self):
        # Frame: PastDate
        past = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertFalse(self.svc.validate_date(past))

    def test_invalid_format(self):
        # Frame: InvalidFormat (wrong separator)
        self.assertFalse(self.svc.validate_date("2026/01/05"))

    def test_non_numeric(self):
        # Frame: NonNumeric
        self.assertFalse(self.svc.validate_date("YYYY-MM-DD"))

    def test_empty_string(self):
        # Frame: EmptyString [error] -> validate_date returns False (caught by except)
        self.assertFalse(self.svc.validate_date(""))


if __name__ == "__main__":
    unittest.main()
