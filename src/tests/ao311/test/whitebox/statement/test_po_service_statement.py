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


class TestPOServiceStatement(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        po_mod.AUDIT_FILE = os.path.join(self._tmpdir.name, "audit_log.txt")

        self.svc = PurchaseOrderService()
        self.svc.repo = FakePORepo()
        self.svc.repo.status_by_id["PO1"] = POStatus.CREATED

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_validate_quantity_statement(self):
        self.assertFalse(self.svc.validate_quantity("1"))
        self.assertFalse(self.svc.validate_quantity(0))
        self.assertTrue(self.svc.validate_quantity(1))

    def test_update_po_status_success_statement(self):
        msg = self.svc.update_po_status("PO1", "APPROVED", "admin")
        self.assertIn("updated successfully", msg)
