from datetime import datetime
from model.purchase_order import PurchaseOrder, PurchaseOrderLine
from Repo.purchase_order_repo import PurchaseOrderRepo
from Repo.product_repo import ProductRepo

class PurchaseOrderService:
    def __init__(self):
        self.repo = PurchaseOrderRepo()
        self.product_repo = ProductRepo()

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
