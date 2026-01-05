"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: PurchaseOrderService.validate_quantity
TSL spec: specs/po_validate_quantity.tsl
"""

import unittest
from Service.purchase_order_service import PurchaseOrderService


class TestPOValidateQuantityTSL(unittest.TestCase):
    def setUp(self):
        self.svc = PurchaseOrderService()

    def test_positive_int(self):
        # Frame: PositiveInt
        self.assertTrue(self.svc.validate_quantity(1))

    def test_zero(self):
        # Frame: Zero [error]
        self.assertFalse(self.svc.validate_quantity(0))

    def test_negative_int(self):
        # Frame: NegativeInt [error]
        self.assertFalse(self.svc.validate_quantity(-3))

    def test_non_int_type(self):
        # Frame: NonIntType [error]
        self.assertFalse(self.svc.validate_quantity("5"))


if __name__ == "__main__":
    unittest.main()
