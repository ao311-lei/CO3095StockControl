"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: PurchaseOrderService.update_po_status
TSL spec: specs/po_update_status.tsl
"""

import unittest
from Service.purchase_order_service import PurchaseOrderService
from model.purchase_order import POStatus


class FakePORepo:
    def __init__(self, existing_status_by_po=None, update_success=True):
        self.status_by_po = existing_status_by_po or {}
        self.update_success = update_success
        self.updated_calls = []

    def get_po_status(self, po_id):
        return self.status_by_po.get(po_id)

    def update_po_status(self, po_id, new_status):
        self.updated_calls.append((po_id, new_status))
        if not self.update_success:
            return False
        if po_id not in self.status_by_po:
            return False
        self.status_by_po[po_id] = new_status
        return True


class TestPOUpdateStatusTSL(unittest.TestCase):
    def setUp(self):
        self.svc = PurchaseOrderService()
        # avoid writing audit files during tests
        self.svc.write_audit = lambda msg: None

    def test_invalid_status_string(self):
        # Frame: StatusInput=InvalidStatus
        self.svc.repo = FakePORepo({"PO1": POStatus.CREATED})
        result = self.svc.update_po_status("PO1", "NOT_A_STATUS", "adora")
        self.assertEqual(result, "Invalid status")

    def test_po_not_found(self):
        # Frame: POExists=No [error]
        self.svc.repo = FakePORepo({})
        result = self.svc.update_po_status("PO404", "APPROVED", "adora")
        self.assertEqual(result, "Purchase Order not found")

    def test_invalid_transition(self):
        # Frame: Transition=Invalid (e.g., CREATED -> COMPLETED is invalid)
        self.svc.repo = FakePORepo({"PO1": POStatus.CREATED})
        result = self.svc.update_po_status("PO1", "COMPLETED", "adora")
        self.assertIn("Invalid transition", result)

    def test_valid_transition_success(self):
        # Frame: ValidLowercase + Transition=Valid (CREATED -> APPROVED)
        self.svc.repo = FakePORepo({"PO1": POStatus.CREATED})
        result = self.svc.update_po_status("PO1", "approved", "adora")
        self.assertEqual(result, "Purchase order PO1 updated successfully")


if __name__ == "__main__":
    unittest.main()
