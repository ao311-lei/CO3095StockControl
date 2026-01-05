"""
CO3095 - White-box (Symbolic Execution)

Unit: Service.purchase_order_service.PurchaseOrderService
Technique: Symbolic Execution for:
- validate_date(): try/except + date >= today
- validate_quantity(): type check + <=0 check
- is_valid_transition(): status branching
- update_po_status(): invalid status, not found, invalid transition, update fail/success

We stub repo and write_audit to avoid filesystem.
"""

from datetime import date, timedelta
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


def make_service():
    svc = PurchaseOrderService()
    svc.repo = FakePORepo()
    svc.write_audit = lambda _msg: None
    return svc


def test_validate_quantity_symbolic_paths():
    svc = make_service()
    assert svc.validate_quantity(1) is True
    assert svc.validate_quantity(0) is False
    assert svc.validate_quantity(-1) is False
    assert svc.validate_quantity("2") is False


def test_validate_date_symbolic_paths():
    svc = make_service()
    today = date.today().strftime("%Y-%m-%d")
    past = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    bad = "not-a-date"

    assert svc.validate_date(today) is True
    assert svc.validate_date(past) is False
    assert svc.validate_date(bad) is False


def test_is_valid_transition_symbolic_paths():
    svc = make_service()

    assert svc.is_valid_transition(POStatus.COMPLETED, POStatus.APPROVED) is False
    assert svc.is_valid_transition(POStatus.CANCELLED, POStatus.CREATED) is False

    assert svc.is_valid_transition(POStatus.CREATED, POStatus.APPROVED) is True
    assert svc.is_valid_transition(POStatus.CREATED, POStatus.PARTIAL) is False

    assert svc.is_valid_transition(POStatus.APPROVED, POStatus.PARTIAL) is True
    assert svc.is_valid_transition(POStatus.APPROVED, POStatus.COMPLETED) is False

    assert svc.is_valid_transition(POStatus.PARTIAL, POStatus.COMPLETED) is True
    assert svc.is_valid_transition(POStatus.PARTIAL, POStatus.APPROVED) is False


def test_update_po_status_symbolic_paths():
    svc = make_service()

    assert svc.update_po_status("PO1", "NOT_A_STATUS", "admin") == "Invalid status"
    assert svc.update_po_status("MISSING", "APPROVED", "admin") == "Purchase Order not found"

    # invalid transition: CREATED -> COMPLETED
    msg = svc.update_po_status("PO1", "COMPLETED", "admin")
    assert "Invalid transition" in msg

    # valid transition: CREATED -> APPROVED
    msg2 = svc.update_po_status("PO1", "APPROVED", "admin")
    assert "updated successfully" in msg2
