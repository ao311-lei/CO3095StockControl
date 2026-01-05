import os
import tempfile
import unittest

from Repo import reservation_repo as rr_mod
from Repo.reservation_repo import ReservationRepo
from model.reservation import Reservation


class TestReservationRepoStatement(unittest.TestCase):
    """Statement testing for Repo.reservation_repo"""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        rr_mod.RESERVATION_FILE = os.path.join(self.tmpdir.name, "reservations.txt")
        self.repo = ReservationRepo()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_reservation_repo_statements(self):
        r = Reservation("RSV1", "O1", "SKU1", 2, 9.99, "adora", "2026-01-05 10:00:00", "ACTIVE")
        self.repo.save_reservation(r)

        all_res = self.repo.get_all_reservations()
        self.assertTrue(len(all_res) >= 1)

        qty = self.repo.get_active_reserved_quantity("SKU1")
        self.assertEqual(qty, 2)

        # cancel path
        self.assertTrue(self.repo.cancel_reservation("RSV1"))
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 0)


if __name__ == "__main__":
    unittest.main()
