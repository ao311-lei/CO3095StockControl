"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: ReservationRepo.get_active_reserved_quantity
TSL spec: specs/reservation_repo_active_qty.tsl
Tool: unittest
"""

import unittest
import tempfile
import os
import importlib

import Repo.reservation_repo  # import the module itself


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


import unittest
import tempfile
import os

import Repo.reservation_repo as reservation_repo_module


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


class TestReservationRepoActiveQtyTSL(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()

        # Override the file path in the SAME imported module
        reservation_repo_module.RESERVATION_FILE = self.tmp.name

        # Create repo from the SAME module object
        self.repo = reservation_repo_module.ReservationRepo()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_none(self):
        write_lines(self.tmp.name, [])
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 0)

    def test_active_match(self):
        write_lines(self.tmp.name, [
            "RSV1|O1|SKU1|2|bob|2026-01-01 10:00:00|ACTIVE|9.99\n"
        ])
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 2)

    def test_cancelled_match_only(self):
        write_lines(self.tmp.name, [
            "RSV1|O1|SKU1|5|bob|2026-01-01 10:00:00|CANCELLED|9.99\n"
        ])
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 0)

    def test_mixed_statuses(self):
        write_lines(self.tmp.name, [
            "RSV1|O1|SKU1|2|bob|t|ACTIVE|9.99\n",
            "RSV2|O1|SKU1|3|bob|t|CANCELLED|9.99\n",
            "RSV3|O1|SKU1|4|bob|t|ACTIVE|9.99\n",
        ])
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 6)

    def test_different_sku_only(self):
        write_lines(self.tmp.name, [
            "RSV1|O1|SKU2|7|bob|t|ACTIVE|9.99\n"
        ])
        self.assertEqual(self.repo.get_active_reserved_quantity("SKU1"), 0)


if __name__ == "__main__":
    unittest.main()
