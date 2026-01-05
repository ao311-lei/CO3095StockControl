import os
import tempfile

import Repo.reservation_repo as rrepo_mod
import Service.reservation_service as rsvc_mod
from Service.reservation_service import ReservationService
from model.user import User


class FakeProductRepo:
    def __init__(self, qty_map):
        self.qty_map = qty_map

    def get_product_quantity(self, sku):
        return self.qty_map.get(sku)


def test_concolic_reserve_flip_fail_to_success(capsys):
    tmpdir = tempfile.TemporaryDirectory()
    try:
        rrepo_mod.RESERVATION_FILE = os.path.join(tmpdir.name, "reservations.txt")
        rsvc_mod.AUDIT_FILE = os.path.join(tmpdir.name, "audit.txt")

        svc = ReservationService(FakeProductRepo({"SKU1": 2}))
        user = User("alice", "pw", "STAFF")

        # seed: quantity too high -> fail
        svc.reserve_stock("O1", "SKU1", 99, user, 1.0)
        assert "Not enough available stock" in capsys.readouterr().out

        # mutate: valid qty -> success
        svc.reserve_stock("O1", "SKU1", 1, user, 1.0)
        assert "Reservation successful" in capsys.readouterr().out
    finally:
        tmpdir.cleanup()
