import os
import tempfile
import unittest

from Repo import purchase_order_repo as po_repo_mod
from Repo.purchase_order_repo import PurchaseOrderRepo
from model.purchase_order import PurchaseOrder, PurchaseOrderLine, POStatus


class TestPurchaseOrderRepoStatement(unittest.TestCase):
    """Statement testing for Repo.purchase_order_repo"""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        po_repo_mod.PO_FILE = os.path.join(self.tmpdir.name, "purchase_orders.txt")
        self.repo = PurchaseOrderRepo()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_purchase_order_repo_statements(self):
        po = PurchaseOrder("PO1", "2026-01-06", "adora", POStatus.CREATED)
        lines = [PurchaseOrderLine("PO1", "SKU1", 3)]
        self.repo.save_purchase_order(po, lines)

        orders = self.repo.get_purchase_orders()
        self.assertTrue(any(o.po_id == "PO1" for o in orders))

        self.assertEqual(self.repo.get_po_status("PO1"), POStatus.CREATED)
        self.assertTrue(self.repo.update_po_status("PO1", POStatus.APPROVED))
        self.assertEqual(self.repo.get_po_status("PO1"), POStatus.APPROVED)


if __name__ == "__main__":
    unittest.main()
