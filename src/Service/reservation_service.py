import uuid
from datetime import datetime, timedelta

from model.reservation import Reservation
from Repo.reservation_repo import ReservationRepo


AUDIT_FILE = "audit_log.txt"


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

    def reserve_stock(self, order_id, sku, quantity, user, expiry_minutes=None):
        # Validation
        if order_id.strip() == "":
            print("Order ID cannot be empty")
            return

        if sku.strip() == "":
            print("SKU cannot be empty")
            return

        if not isinstance(quantity, int) or quantity <= 0:
            print("Quantity must be a positive integer")
            return

        if not self.product_repo.is_product_active(sku):
            print("Product is inactive or does not exist")
            return

        available = self.get_available_quantity(sku)
        if available is None:
            print("Product not found")
            return

        # Role override
        role = getattr(user, "role", "staff").lower()
        can_override = (role == "admin")

        if quantity > available and not can_override:
            print(f"Not enough available stock. Available: {available}")
            return

        reservation_id = "RSV-" + uuid.uuid4().hex[:6].upper()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        expires_at = ""
        if expiry_minutes is not None:
            exp = datetime.now() + timedelta(minutes=int(expiry_minutes))
            expires_at = exp.strftime("%Y-%m-%d %H:%M:%S")

        reservation = Reservation(
            reservation_id,
            order_id,
            sku,
            quantity,
            user.username,
            created_at,
            "ACTIVE",
            expires_at
        )

        self.reservation_repo.save_reservation(reservation)
        self.write_audit(
            f"Reservation {reservation_id} created by {user.username} "
            f"order={order_id} sku={sku} qty={quantity}"
        )

        print(f"Reservation successful. ID: {reservation_id}")

    def cancel_reservation(self, reservation_id, user):
        if self.reservation_repo.cancel_reservation(reservation_id):
            self.write_audit(f"Reservation {reservation_id} cancelled by {user.username}")
            print("Reservation cancelled and stock released")
        else:
            print("Reservation not found or already cancelled")