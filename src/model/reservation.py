class Reservation:
    def __init__(self, reservation_id, order_id,sku,quantity,price,created_by, created_at,status="ACTIVE"):
        self.reservation_id = reservation_id
        self.order_id = order_id
        self.sku = sku
        self.quantity = int(quantity)
        self.price = price
        self.created_by = created_by
        self.created_at = created_at
        self.status = status
