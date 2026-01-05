import os
import tempfile
from datetime import date, timedelta

import Service.purchase_order_service as svc_mod
from Service.purchase_order_service import PurchaseOrderService
from model.purchase_order import POStatus


class FakePORepo:
    def __init__(self):
        self.status_by_id = {"PO1": POStatus.CREATED}

    def get_po_status(self, po_id):
        return self.status_by_id.get(po_id)

    def update_po_status(self, po_id, new_status):
        if po_id not in self.status_by_id:
            return False
        self.status_by_id[po_id] = new_status
        return True


def make_service(audit_path):
    svc = PurchaseOrderService.__new__(PurchaseOrderService)
    svc.repo = FakePORepo()
    svc_mod.AUDIT_FILE = audit_path
    return svc


def test_concolic_validate_date_flip():
    tmpdir = tempfile.TemporaryDirectory()
    try:
        svc = make_service(os.path.join(tmpdir.name, "audit.txt"))
        past = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = date.today().strftime("%Y-%m-%d")

        # seed: invalid (past) -> False
        assert svc.validate_date(past) is False
        # mutate: valid -> True
        assert svc.validate_date(today) is True
    finally:
        tmpdir.cleanup()


def test_concolic_update_po_status_flip_invalid_to_valid():
    tmpdir = tempfile.TemporaryDirectory()
    try:
        svc = make_service(os.path.join(tmpdir.name, "audit.txt"))

        # seed: invalid status
        assert svc.update_po_status("PO1", "BAD", "admin") == "Invalid status"

        # mutate: valid status but invalid transition (CREATED->COMPLETED)
        msg = svc.update_po_status("PO1", "COMPLETED", "admin")
        assert "Invalid transition" in msg

        # mutate: valid transition (CREATED->APPROVED)
        msg2 = svc.update_po_status("PO1", "APPROVED", "admin")
        assert "updated successfully" in msg2
    finally:
        tmpdir.cleanup()
