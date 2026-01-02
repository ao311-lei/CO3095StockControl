import uuid
from datetime import datetime

from model.reservation import Reservation
from Repo.reservation_repo import ReservationRepo


AUDIT_FILE = "src/data/audit_log.txt"


class ReservationService:

    def __init__(self, product_repo):
        self.product_repo = product_repo
        self.reservation_repo = ReservationRepo()

    def write_audit(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(AUDIT_FILE, "a") as file:
            file.write(f"{timestamp} - {message}\n")

    def get_available_quantity(self, sku):
        on_hand = self.product_repo.get_product_quantity(sku)
        if on_hand is None:
            return None

        reserved = self.reservation_repo.get_active_reserved_quantity(sku)
        return on_hand - reserved

    def reserve_stock(self, order_id, sku, quantity, user=None, price=None):
        if order_id.strip() == "":
            print("Order ID cannot be empty")
            return

        if sku.strip() == "":
            print("SKU cannot be empty")
            return

        if not isinstance(quantity, int) or quantity <= 0:
            print("Quantity must be a positive integer")
            return

        available = self.get_available_quantity(sku)
        if available is None:
            print("Product not found")
            return


        if quantity > available:
            print(f"Not enough available stock. Available: {available}")
            return

        reservation_id = "RSV-" + uuid.uuid4().hex[:6].upper()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        reservation = Reservation(
            reservation_id,
            order_id,
            sku,
            quantity,
            price,
            user.username,
            created_at,
            "ACTIVE",
        )

        self.reservation_repo.save_reservation(reservation)
        self.write_audit(f"USER={user} ACTION=RESERVATION sku={sku} order={order_id} qty={quantity}")

        print(f"Reservation successful. ID: {reservation_id}")

    def cancel_reservation(self, reservation_id, user):
        if self.reservation_repo.cancel_reservation(reservation_id):
            self.write_audit(f"Reservation {reservation_id} cancelled by {user.username}")
            print("Reservation cancelled and stock released")
        else:
            print("Reservation not found or already cancelled")

    def get_reservation(self):
        return self.reservation_repo.get_all_reservations()
