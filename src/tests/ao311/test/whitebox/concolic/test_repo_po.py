import os
import tempfile

import Repo.purchase_order_repo as po_mod
from Repo.purchase_order_repo import PurchaseOrderRepo
from model.purchase_order import PurchaseOrder, PurchaseOrderLine, POStatus


def test_concolic_po_repo_update_flip_fail_to_success():
    tmpdir = tempfile.TemporaryDirectory()
    try:
        po_mod.PO_FILE = os.path.join(tmpdir.name, "po.txt")
        repo = PurchaseOrderRepo()

        # seed: update non-existing -> False
        assert repo.update_po_status("PO1", POStatus.APPROVED) is False

        # mutate: create PO then update -> True
        po = PurchaseOrder("PO1", "2026-01-06", "adora", POStatus.CREATED)
        repo.save_purchase_order(po, [PurchaseOrderLine("PO1", "SKU1", 1)])

        assert repo.update_po_status("PO1", POStatus.APPROVED) is True
        assert repo.get_po_status("PO1") == POStatus.APPROVED
    finally:
        tmpdir.cleanup()
