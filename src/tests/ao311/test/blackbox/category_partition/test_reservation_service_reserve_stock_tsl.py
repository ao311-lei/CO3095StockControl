"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: ReservationService.reserve_stock
TSL spec: specs/reservation_reserve_stock.tsl

Note: reserve_stock returns None and prints messages,
so we assert behavioural effects:
- save_reservation called / not called
"""

import unittest
from Service.reservation_service import ReservationService


class FakeUser:
    def __init__(self, username):
        self.username = username


class FakeProductRepo:
    def __init__(self, quantities):
        self.quantities = quantities

    def get_product_quantity(self, sku):
        return self.quantities.get(sku)


class FakeReservationRepo:
    def __init__(self, reserved_by_sku=None):
        self.reserved_by_sku = reserved_by_sku or {}
        self.saved = []

    def get_active_reserved_quantity(self, sku):
        return self.reserved_by_sku.get(sku, 0)

    def save_reservation(self, reservation):
        self.saved.append(reservation)


class TestReservationServiceReserveStockTSL(unittest.TestCase):
    def setUp(self):
        self.user = FakeUser("adora")

    def test_order_id_empty(self):
        # Frame: OrderID=Empty [error]
        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        svc.reservation_repo = FakeReservationRepo({})
        svc.write_audit = lambda msg: None
        svc.reserve_stock("", "SKU1", 1, self.user, 9.99)
        self.assertEqual(len(svc.reservation_repo.saved), 0)

    def test_sku_empty(self):
        # Frame: SKU=Empty [error]
        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        svc.reservation_repo = FakeReservationRepo({})
        svc.write_audit = lambda msg: None
        svc.reserve_stock("O1", "", 1, self.user, 9.99)
        self.assertEqual(len(svc.reservation_repo.saved), 0)

    def test_quantity_non_int(self):
        # Frame: Quantity=NonInt [error]
        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        svc.reservation_repo = FakeReservationRepo({})
        svc.write_audit = lambda msg: None
        svc.reserve_stock("O1", "SKU1", "2", self.user, 9.99)
        self.assertEqual(len(svc.reservation_repo.saved), 0)

    def test_product_missing(self):
        # Frame: SKU=ValidMissing [error]
        svc = ReservationService(FakeProductRepo({}))
        svc.reservation_repo = FakeReservationRepo({})
        svc.write_audit = lambda msg: None
        svc.reserve_stock("O1", "SKU1", 1, self.user, 9.99)
        self.assertEqual(len(svc.reservation_repo.saved), 0)

    def test_quantity_exceeds_available(self):
        # Frame: PositiveExceedsAvailable [error]
        svc = ReservationService(FakeProductRepo({"SKU1": 2}))
        svc.reservation_repo = FakeReservationRepo({"SKU1": 1})  # available = 1
        svc.write_audit = lambda msg: None
        svc.reserve_stock("O1", "SKU1", 2, self.user, 9.99)
        self.assertEqual(len(svc.reservation_repo.saved), 0)

    def test_success_within_available(self):
        # Frame: PositiveWithinAvailable
        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        svc.reservation_repo = FakeReservationRepo({"SKU1": 3})  # available=7
        svc.write_audit = lambda msg: None
        svc.reserve_stock("O1", "SKU1", 2, self.user, 9.99)
        self.assertEqual(len(svc.reservation_repo.saved), 1)


if __name__ == "__main__":
    unittest.main()
