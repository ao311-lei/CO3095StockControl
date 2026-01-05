"""
CO3095 - Symbolic Execution (White-box)

Unit: Service.reservation_service.ReservationService
Functions:
- __init__
- write_audit
- get_available_quantity
- reserve_stock
- cancel_reservation
- get_reservation

We patch reservation file and audit file to temp.
"""

import os
import tempfile

import Repo.reservation_repo as rrepo_mod
import Service.reservation_service as rsvc_mod

from Repo.reservation_repo import ReservationRepo
from Service.reservation_service import ReservationService
from model.user import User


class FakeProductRepo:
    def __init__(self, qty_map):
        self.qty_map = qty_map

    def get_product_quantity(self, sku):
        return self.qty_map.get(sku)


def test_reservation_service_symbolic_all_functions(capsys):
    tmpdir = tempfile.TemporaryDirectory()
    try:
        # patch module-level files
        rrepo_mod.RESERVATION_FILE = os.path.join(tmpdir.name, "reservations.txt")
        rsvc_mod.AUDIT_FILE = os.path.join(tmpdir.name, "audit_log.txt")

        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        user = User("alice", "pw", "STAFF")

        # get_available_quantity: product missing => None
        assert svc.get_available_quantity("MISSING") is None

        # reserve_stock: empty order id
        svc.reserve_stock("  ", "SKU1", 1, user, 1.0)
        assert "Order ID cannot be empty" in capsys.readouterr().out

        # reserve_stock: empty sku
        svc.reserve_stock("O1", "  ", 1, user, 1.0)
        assert "SKU cannot be empty" in capsys.readouterr().out

        # reserve_stock: invalid qty
        svc.reserve_stock("O1", "SKU1", 0, user, 1.0)
        assert "Quantity must be a positive integer" in capsys.readouterr().out

        # reserve_stock: product not found
        svc.reserve_stock("O1", "MISSING", 1, user, 1.0)
        assert "Product not found" in capsys.readouterr().out

        # reserve_stock: not enough available
        svc.reserve_stock("O1", "SKU1", 99, user, 1.0)
        assert "Not enough available stock" in capsys.readouterr().out

        # reserve_stock: success
        svc.reserve_stock("O1", "SKU1", 2, user, 1.0)
        out = capsys.readouterr().out
        assert "Reservation successful" in out

        # get_reservation (calls repo.get_all_reservations)
        res = svc.get_reservation()
        assert len(res) == 1

        # cancel_reservation: get reservation id from file
        with open(rrepo_mod.RESERVATION_FILE, "r", encoding="utf-8") as f:
            rid = f.readline().split("|")[0]

        svc.cancel_reservation(rid, user)
        assert "Reservation cancelled" in capsys.readouterr().out

        # cancel_reservation again => not found/already cancelled
        svc.cancel_reservation(rid, user)
        assert "not found" in capsys.readouterr().out.lower()

        # write_audit direct
        svc.write_audit("hello")
        assert os.path.exists(rsvc_mod.AUDIT_FILE)

    finally:
        tmpdir.cleanup()
