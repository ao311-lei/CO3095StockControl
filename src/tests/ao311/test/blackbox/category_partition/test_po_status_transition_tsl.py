"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: PurchaseOrderService.is_valid_transition
TSL spec: specs/po_status_transition.tsl
"""

import unittest
from Service.purchase_order_service import PurchaseOrderService
from model.purchase_order import POStatus


class TestPOStatusTransitionTSL(unittest.TestCase):
    def setUp(self):
        self.svc = PurchaseOrderService()

    def test_completed_is_terminal(self):
        # Frame: Current=Completed, New=Approved (any new should be False)
        self.assertFalse(self.svc.is_valid_transition(POStatus.COMPLETED, POStatus.APPROVED))

    def test_cancelled_is_terminal(self):
        # Frame: Current=Cancelled, New=Completed
        self.assertFalse(self.svc.is_valid_transition(POStatus.CANCELLED, POStatus.COMPLETED))

    def test_created_to_approved_valid(self):
        # Frame: Current=Created, New=Approved
        self.assertTrue(self.svc.is_valid_transition(POStatus.CREATED, POStatus.APPROVED))

    def test_created_to_partial_invalid(self):
        # Frame: Current=Created, New=Partial
        self.assertFalse(self.svc.is_valid_transition(POStatus.CREATED, POStatus.PARTIAL))

    def test_approved_to_partial_valid(self):
        # Frame: Current=Approved, New=Partial
        self.assertTrue(self.svc.is_valid_transition(POStatus.APPROVED, POStatus.PARTIAL))

    def test_partial_to_completed_valid(self):
        # Frame: Current=Partial, New=Completed
        self.assertTrue(self.svc.is_valid_transition(POStatus.PARTIAL, POStatus.COMPLETED))


if __name__ == "__main__":
    unittest.main()
