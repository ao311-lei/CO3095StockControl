"""
CO3095 - Black-box Category Partition (TSLGenerator derived)
Target: ReservationService.get_available_quantity
TSL spec: specs/reservation_available_qty.tsl
"""

import unittest
from Service.reservation_service import ReservationService


class FakeProductRepo:
    def __init__(self, quantities):
        self.quantities = quantities  # sku -> on_hand

    def get_product_quantity(self, sku):
        return self.quantities.get(sku)


class FakeReservationRepo:
    def __init__(self, reserved_by_sku):
        self.reserved_by_sku = reserved_by_sku

    def get_active_reserved_quantity(self, sku):
        return self.reserved_by_sku.get(sku, 0)


class TestReservationServiceAvailableQtyTSL(unittest.TestCase):
    def test_missing_product_returns_none(self):
        # Frame: SKU=Missing [error]
        svc = ReservationService(FakeProductRepo({}))
        svc.reservation_repo = FakeReservationRepo({"SKU1": 2})
        self.assertIsNone(svc.get_available_quantity("SKU1"))

    def test_exists_none_reserved(self):
        # Frame: Exists + Reserved=None
        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        svc.reservation_repo = FakeReservationRepo({})
        self.assertEqual(svc.get_available_quantity("SKU1"), 10)

    def test_exists_some_active_reserved(self):
        # Frame: Exists + Reserved=SomeActive
        svc = ReservationService(FakeProductRepo({"SKU1": 10}))
        svc.reservation_repo = FakeReservationRepo({"SKU1": 3})
        self.assertEqual(svc.get_available_quantity("SKU1"), 7)


if __name__ == "__main__":
    unittest.main()
