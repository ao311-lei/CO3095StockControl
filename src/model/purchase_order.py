class PurchaseOrder:
    def __init__(self, po_id, expected_date, created_by, status):
        self.po_id = po_id
        self.expected_date = expected_date
        self.created_by = created_by
        self.status = status

class PurchaseOrderLine:
    def __init__(self, po_id, sku, quantity):
        self.po_id = po_id
        self.sku = sku
        self.quantity = quantity

class POStatus:
    CREATED = 'CREATED'
    APPROVED = 'APPROVED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    ALL = (CREATED, APPROVED, COMPLETED, CANCELLED)
