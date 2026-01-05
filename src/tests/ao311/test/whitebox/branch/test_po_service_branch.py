import os
import tempfile
import unittest

from Service.purchase_order_service import PurchaseOrderService
from Service import purchase_order_service as po_mod
from model.purchase_order import POStatus


class FakePORepo:
    def __init__(self):
        self.status_by_id = {}

    def get_po_status(self, po_id):
        return self.status_by_id.get(po_id)

    def update_po_status(self, po_id, new_status):
        if po_id not in self.status_by_id:
            return False
        self.status_by_id[po_id] = new_status
        return True


class TestPurchaseOrderServiceBranch(unittest.TestCase):
    """
    White-box Branch Testing (Lecture 9 / Lab 9)

    Covers branches in:
    - validate_quantity
    - is_valid_transition
    - update_po_status (invalid status, not found, invalid transition, update fail, success)
    """

    def setUp(self):
        # Patch audit file to a temp location so write_audit never fails
        self._tmpdir = tempfile.TemporaryDirectory()
        po_mod.AUDIT_FILE = os.path.join(self._tmpdir.name, "audit_log.txt")

        self.svc = PurchaseOrderService()
        self.svc.repo = FakePORepo()  # patch repo
        self.svc.repo.status_by_id["PO1"] = POStatus.CREATED

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_validate_quantity_branches(self):
        self.assertFalse(self.svc.validate_quantity("3"))
        self.assertFalse(self.svc.validate_quantity(0))
        self.assertFalse(self.svc.validate_quantity(-1))
        self.assertTrue(self.svc.validate_quantity(1))

    def test_is_valid_transition_branches(self):
        self.assertFalse(self.svc.is_valid_transition(POStatus.COMPLETED, POStatus.CANCELLED))
        self.assertTrue(self.svc.is_valid_transition(POStatus.CREATED, POStatus.APPROVED))
        self.assertFalse(self.svc.is_valid_transition(POStatus.CREATED, POStatus.COMPLETED))

    def test_update_po_status_invalid_status(self):
        msg = self.svc.update_po_status("PO1", "NOTREAL", "admin")
        self.assertEqual(msg, "Invalid status")

    def test_update_po_status_not_found(self):
        msg = self.svc.update_po_status("PO404", "APPROVED", "admin")
        self.assertEqual(msg, "Purchase Order not found")

    def test_update_po_status_invalid_transition(self):
        msg = self.svc.update_po_status("PO1", "COMPLETED", "admin")
        self.assertIn("Invalid transition", msg)

    def test_update_po_status_update_fail(self):
        self.svc.repo.status_by_id["POX"] = POStatus.CREATED

        def fail_update(_po_id, _st):
            return False

        self.svc.repo.update_po_status = fail_update
        msg = self.svc.update_po_status("POX", "APPROVED", "admin")
        self.assertEqual(msg, "Purchase Order not updated")

    def test_update_po_status_success(self):
        msg = self.svc.update_po_status("PO1", "APPROVED", "admin")
        self.assertIn("updated successfully", msg)
        self.assertEqual(self.svc.repo.status_by_id["PO1"], "APPROVED")


if __name__ == "__main__":
    unittest.main()
