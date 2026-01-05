"""
CO3095 - White-box (Symbolic Execution)

Unit: Repo.reservation_repo.ReservationRepo
Technique: Symbolic Execution for:
- get_all_reservations(): len(parts)!=8 skip, file missing path
- get_active_reserved_quantity(): sum only ACTIVE
- cancel_reservation(): file missing false, update true, no match false
"""

import os
import tempfile

import Repo.reservation_repo as reservation_repo_module
from Repo.reservation_repo import ReservationRepo


def test_get_all_reservations_file_missing_path(tmp_path):
    # point module constant to a missing file
    reservation_repo_module.RESERVATION_FILE = str(tmp_path / "missing.txt")
    repo = ReservationRepo()
    assert repo.get_all_reservations() == []


def test_active_reserved_quantity_paths(tmp_path):
    f = tmp_path / "reservations.txt"
    reservation_repo_module.RESERVATION_FILE = str(f)

    # 8 fields:
    # id|order|sku|qty|created_by|created_at|status|price
    f.write_text(
        "R1|O1|SKU1|2|u|t|ACTIVE|9.99\n"
        "R2|O1|SKU1|4|u|t|CANCELLED|9.99\n"
        "R3|O1|SKU2|5|u|t|ACTIVE|9.99\n"
        "BAD_LINE_NOT_8_FIELDS\n"
    )

    repo = ReservationRepo()
    assert repo.get_active_reserved_quantity("SKU1") == 2
    assert repo.get_active_reserved_quantity("SKU2") == 5
    assert repo.get_active_reserved_quantity("MISSING") == 0


def test_cancel_reservation_paths(tmp_path):
    f = tmp_path / "reservations.txt"
    reservation_repo_module.RESERVATION_FILE = str(f)

    f.write_text(
        "R1|O1|SKU1|2|u|t|ACTIVE|9.99\n"
        "R2|O1|SKU1|4|u|t|CANCELLED|9.99\n"
    )
    repo = ReservationRepo()

    assert repo.cancel_reservation("R1") is True
    updated = f.read_text()
    assert "R1|O1|SKU1|2|u|t|CANCELLED|9.99" in updated

    # already cancelled -> should remain false
    assert repo.cancel_reservation("R2") is False
    # not found -> false
    assert repo.cancel_reservation("RX") is False
