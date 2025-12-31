import uuid
from datetime import datetime,date
from model.purchase_order import PurchaseOrder, PurchaseOrderLine,POStatus
from Repo.purchase_order_repo import PurchaseOrderRepo
from Repo.product_repo import ProductRepo

AUDIT_FILE = 'audit_log.txt'

class PurchaseOrderService:
    def __init__(self):
        self.repo = PurchaseOrderRepo()
        self.product_repo = ProductRepo('products.txt')

    def validate_date(self, date_string):
        try:
            year, month, day = date_string.split("-")
            delivery_date = date(int(year),int(month), int(day))
            return delivery_date >= date.today()
        except:
            return False

    def validate_quantity(self, quantity):
        if not isinstance(quantity, int):
            return False
        if quantity <= 0:
            return False
        return True

    def create_purchase_order(self, expected_date, product_lines,user):
        if not self.validate_date(expected_date):
            print("Invalid expected delivery date")
            return

        if len(product_lines) == 0:
            print("Purchase order must have at least one product")
            return

        valid_lines = []
        for line in product_lines:
            sku = line['sku']
            quantity = line['quantity']

        valid_lines.append((sku, quantity))

        if len(valid_lines) == 0:
            print("Purchase order must have at least one product")
            return

        po_id = "PO" + datetime.now().strftime("%Y%m%d%H%M%S")
        po = PurchaseOrder(po_id, expected_date, user, "CREATED")

        line_objects = []
        for sku, quantity in valid_lines:
            line_objects.append(PurchaseOrderLine(po_id, sku, quantity))

        self.repo.save_purchase_order(po, line_objects)
        self.write_audit(f"PO {po_id}, created by {user}")
        print(f"Purchase order {po_id} created successfully")

    def get_purchase_order(self):
        return self.repo.get_purchase_orders()
    def is_valid_transition(self, current, new):
        if current in [POStatus.COMPLETED, POStatus.CANCELLED]:
            return False

        if current == POStatus.CREATED:
            return new in [POStatus.APPROVED, POStatus.CANCELLED]

        if current == POStatus.APPROVED:
            return new in [POStatus.PARTIAL, POStatus.CANCELLED]

        if current == POStatus.PARTIAL:
            return new in [POStatus.COMPLETED, POStatus.CANCELLED]

        return False
    def update_po_status(self, po_id, status, user):
        status = status.strip().upper()

        if status not in POStatus.ALL:
            return "Invalid status"

        current_status = self.repo.get_po_status(po_id)
        if current_status is None:
            return "Purchase Order not found"

        if not self.is_valid_transition(current_status, status):
            return "Invalid transition:{current_status} to {status}"

        updated = self.repo.update_po_status(po_id, status)
        if not updated:
            return "Purchase Order not updated"

        self.write_audit(f"Purchase order {po_id} updated successfully by {user}")
        return f"Purchase order {po_id} updated successfully"

    def write_audit(self, message):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(AUDIT_FILE, "a") as file:
            file.write(f"{timestamp} {message}\n")



