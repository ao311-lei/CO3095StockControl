import uuid
from datetime import datetime,date
from model.purchase_order import PurchaseOrder, PurchaseOrderLine
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

            if not self.product_repo.product_active(sku):
                print(f"Product {sku} not active")
                continue

            valid_lines.append((sku, quantity))

        if len(valid_lines) == 0:
            print("Purchase order must have at least one product")
            return

        po_id = "PO" + datetime.now().strftime("%Y%m%d%H%M%S")
        po = PurchaseOrder(po_id, expected_date, user, "DRAFT")

        line_objects = []
        for sku, quantity in valid_lines:
            line_objects.append(PurchaseOrderLine(po_id, sku, quantity))

        self.repo.save_purchase_order(po, line_objects)
        self.write_audit(f"PO {po_id}, created by {user}")
        print(f"Purchase order {po_id} created successfully")

    def get_purchase_order(self):
        return self.repo.get_purchase_order()

    def write_audit(self, message):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(AUDIT_FILE, "a") as file:
            file.write(f"{timestamp} {message}\n")



