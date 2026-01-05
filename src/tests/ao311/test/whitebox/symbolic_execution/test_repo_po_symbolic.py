"""
CO3095 - Symbolic Execution (White-box)

Unit: Repo.purchase_order_repo.PurchaseOrderRepo
Functions:
- save_purchase_order()
- get_purchase_orders()
- get_po_status()
- update_po_status()

We patch PO_FILE to a temp file.
"""

import os
import tempfile

import Repo.purchase_order_repo as po_mod
from Repo.purchase_order_repo import PurchaseOrderRepo
from model.purchase_order import PurchaseOrder, PurchaseOrderLine, POStatus


def test_purchase_order_repo_symbolic_all_functions():
    tmpdir = tempfile.TemporaryDirectory()
    try:
        po_mod.PO_FILE = os.path.join(tmpdir.name, "purchase_orders.txt")

        repo = PurchaseOrderRepo()

        po = PurchaseOrder("PO1", "2026-01-06", "adora", POStatus.CREATED)
        lines = [PurchaseOrderLine("PO1", "SKU1", 3)]
        repo.save_purchase_order(po, lines)

        orders = repo.get_purchase_orders()
        assert len(orders) == 1
        assert orders[0].po_id == "PO1"

        status = repo.get_po_status("PO1")
        assert status == POStatus.CREATED

        # update success
        assert repo.update_po_status("PO1", POStatus.APPROVED) is True
        assert repo.get_po_status("PO1") == POStatus.APPROVED

        # update fail
        assert repo.update_po_status("MISSING", POStatus.APPROVED) is False
    finally:
        tmpdir.cleanup()
