import os
import tempfile
import unittest

from Service import reservation_service as rsvc_mod
from Repo import reservation_repo as rrepo_mod
from Service.reservation_service import ReservationService
from model.user import User


class FakeProductRepo:
    def __init__(self, qty_by_sku):
        self.qty_by_sku = qty_by_sku

    def get_product_quantity(self, sku):
        return self.qty_by_sku.get(sku)


class TestReservationServiceStatement(unittest.TestCase):
    """Statement testing for Service.reservation_service"""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

        # Patch file constants
        rsvc_mod.AUDIT_FILE = os.path.join(self.tmpdir.name, "audit_log.txt")
        rrepo_mod.RESERVATION_FILE = os.path.join(self.tmpdir.name, "reservations.txt")

        self.product_repo = FakeProductRepo({"SKU1": 10})
        self.svc = ReservationService(self.product_repo)

        self.user = User("alice", "pw", "STAFF")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_reservation_service_statements(self):
        # get_available_quantity executes on_hand/reserved logic
        available = self.svc.get_available_quantity("SKU1")
        self.assertEqual(available, 10)

        # reserve stock (happy path)
        self.svc.reserve_stock("O1", "SKU1", 2, self.user, 9.99)

        # after reservation, available decreases
        available2 = self.svc.get_available_quantity("SKU1")
        self.assertEqual(available2, 8)

        # cancel (grab reservation id from file)
        with open(rrepo_mod.RESERVATION_FILE, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        reservation_id = first_line.split("|")[0]

        self.svc.cancel_reservation(reservation_id, self.user)

        # now should be back to 10 active reserved qty = 0
        available3 = self.svc.get_available_quantity("SKU1")
        self.assertEqual(available3, 10)


if __name__ == "__main__":
    unittest.main()
