import os
import tempfile
import unittest
from Repo import reservation_repo as rr
from Repo.reservation_repo import ReservationRepo
from model.reservation import Reservation


class TestReservationRepoBranch(unittest.TestCase):
    """
    Branch testing for ReservationRepo:
    - get_all_reservations: FileNotFound -> []
    - parsing: skip malformed lines
    - get_active_reserved_quantity: sums ACTIVE only
    - cancel_reservation: file missing -> False
    - cancel_reservation: not found -> False
    - cancel_reservation: found ACTIVE -> True (status changed)
    """

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.tmpdir.name, "reservations.txt")

        # Patch module constant to point at our temp file
        rr.RESERVATION_FILE = self.filepath

        self.repo = ReservationRepo()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_lines(self, lines):
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))

    def test_get_all_reservations_file_missing(self):
        # ensure file doesn't exist
        if os.path.exists(self.filepath):
            os.unlink(self.filepath)
        self.assertEqual(self.repo.get_all_reservations(), [])

    def test_get_all_reservations_skips_bad_lines(self):
        self._write_lines(["bad|line", "RSV1|O1|SKU1|2|alice|2026|ACTIVE|9.99"])
        res = self.repo.get_all_reservations()
        self.assertEqual(len(res), 1)

    def test_get_active_reserved_quantity_sums_active(self):
        self._write_lines([
            "RSV1|O1|SKU1|2|alice|2026|ACTIVE|9.99",
            "RSV2|O1|SKU1|4|alice|2026|CANCELLED|9.99",
            "RSV3|O1|SKU2|3|alice|2026|ACTIVE|9.99",
        ])
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 2)
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU2"), 3)

    def test_cancel_reservation_file_missing(self):
        if os.path.exists(self.filepath):
            os.unlink(self.filepath)
        self.assertFalse(self.repo.cancel_reservation("RSV1"))

    def test_cancel_reservation_not_found(self):
        self._write_lines(["RSV1|O1|SKU1|2|alice|2026|ACTIVE|9.99"])
        self.assertFalse(self.repo.cancel_reservation("RSV999"))

    def test_cancel_reservation_success(self):
        self._write_lines(["RSV1|O1|SKU1|2|alice|2026|ACTIVE|9.99"])
        self.assertTrue(self.repo.cancel_reservation("RSV1"))
        # verify status flipped
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 0)


if __name__ == "__main__":
    unittest.main()
