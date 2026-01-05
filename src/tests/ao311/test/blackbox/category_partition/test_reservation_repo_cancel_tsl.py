"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: ReservationRepo.cancel_reservation
TSL spec: specs/reservation_repo_cancel.tsl
"""

import unittest
import tempfile
import os

import Repo.reservation_repo as rr
from Repo.reservation_repo import ReservationRepo


class TestReservationRepoCancelTSL(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        rr.RESERVATION_FILE = self.tmp.name
        self.repo = ReservationRepo()

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_missing_file_returns_false(self):
        # Frame: FileState=Missing [error]
        os.unlink(self.tmp.name)
        self.assertFalse(self.repo.cancel_reservation("RSV1"))

    def test_active_exists_updates_true(self):
        # Frame: ActiveExists
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("RSV1|O1|SKU1|2|bob|t|ACTIVE|9.99\n")
        self.assertTrue(self.repo.cancel_reservation("RSV1"))

        # verify file updated
        with open(self.tmp.name, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("|CANCELLED|", content)

    def test_cancelled_exists_returns_false(self):
        # Frame: CancelledExists
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("RSV1|O1|SKU1|2|bob|t|CANCELLED|9.99\n")
        self.assertFalse(self.repo.cancel_reservation("RSV1"))

    def test_not_found_returns_false(self):
        # Frame: NotFound
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("RSV2|O1|SKU1|2|bob|t|ACTIVE|9.99\n")
        self.assertFalse(self.repo.cancel_reservation("RSV1"))

    def test_malformed_lines_ignored(self):
        # Frame: MalformedLines
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("BADLINE\n")
            f.write("RSV1|O1|SKU1|2|bob|t|ACTIVE|9.99\n")
        self.assertTrue(self.repo.cancel_reservation("RSV1"))


if __name__ == "__main__":
    unittest.main()
