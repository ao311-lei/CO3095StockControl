import uuid
from datetime import datetime, date
from model.purchase_order import PurchaseOrder, PurchaseOrderLine, POStatus
from Repo.purchase_order_repo import PurchaseOrderRepo
from Repo.product_repo import ProductRepo

AUDIT_FILE = "audit_log.txt"

class PurchaseOrderService:
    def __init__(self):
        self.repo = PurchaseOrderRepo()
        self.product_repo = ProductRepo("products.txt")

    def validate_date(self, date_string):
        try:
            year, month, day = date_string.split("-")
            delivery_date = date(int(year), int(month), int(day))
            return delivery_date >= date.today()
        except:
            return False

    def validate_quantity(self, quantity):
        if not isinstance(quantity, int):
            return False
        if quantity <= 0:
            return False
        return True

    def _get_monthly_budget_amount(self, budget_service):

        if budget_service is None:
            return None, None

        month_key = budget_service.budget_repo.current_month_key()

        saved_month, saved_budget, _spent = budget_service.budget_repo.load_budget_record()

        if saved_month is None or saved_budget is None:
            return month_key, None

        if saved_month != month_key:
            return month_key, None

        return month_key, float(saved_budget)

    def _print_budget_after_purchase(self, budget_service):
        if budget_service is None:
            return

        try:
            month_key = budget_service.budget_repo.current_month_key()
            saved_month, saved_budget, saved_spent = budget_service.budget_repo.load_budget_record()

            if saved_month is None or saved_budget is None:
                return

            if saved_month != month_key:
                return

            if saved_spent is None:
                saved_spent = 0.0

            remaining = float(saved_budget) - float(saved_spent)

            print(f"Remaining budget for {month_key}: £{remaining:.2f}")

        except:
            return

    def create_purchase_order(self, expected_date, product_lines, user, budget_service=None):
        if not self.validate_date(expected_date):
            print("Invalid expected delivery date")
            return

        if len(product_lines) == 0:
            print("Purchase order must have at least one product")
            return

        valid_lines = []
        total_cost = 0.0

        for line in product_lines:
            sku = line["sku"]
            quantity = line["quantity"]

            product = self.product_repo.find_by_sku(sku)

            if product is None:
                print(f"Product {sku} not found. Line skipped.")
                continue

            if getattr(product, "active", True) is False:
                print(f"Product {sku} is INACTIVE. Line skipped.")
                continue

            if not self.validate_quantity(quantity):
                print(f"Invalid quantity for {sku}. Line skipped.")
                continue

            try:
                line_cost = float(product.price) * int(quantity)
                total_cost += line_cost
            except:
                print(f"Could not calculate cost for {sku}. Line skipped.")
                continue

            valid_lines.append((sku, quantity))

        if len(valid_lines) == 0:
            print("Purchase order must have at least one valid product")
            return

        month_key, budget = self._get_monthly_budget_amount(budget_service)

        if budget is None:

            if month_key is None:
                print(f"\nPO cost: £{total_cost:.2f}")
                print("Warning: No monthly budget set yet.")
            else:
                print(f"\nPO cost: £{total_cost:.2f}")
                print(f"Warning: No budget set for {month_key} yet.")
        else:
            print(f"\nPO cost: £{total_cost:.2f}")
            print(f"Monthly budget for {month_key}: £{budget:.2f}")

            if total_cost > budget:
                print("Purchase order blocked: estimated cost exceeds the monthly budget.")
                self.write_audit(
                    f"PO BLOCKED (over budget) - User: {user}, Cost: £{total_cost:.2f}, Budget: £{budget:.2f}"
                )
                return

        po_id = "PO" + datetime.now().strftime("%Y%m%d%H%M%S")
        po = PurchaseOrder(po_id, expected_date, user, "CREATED")

        line_objects = []
        for sku, quantity in valid_lines:
            line_objects.append(PurchaseOrderLine(po_id, sku, quantity))

        self.repo.save_purchase_order(po, line_objects)
        self._add_to_budget_spent(budget_service, total_cost)
        self._print_budget_after_purchase(budget_service)
        self.write_audit(f"PO {po_id}, created by {user} (Cost: £{total_cost:.2f})")
        print(f"Purchase order {po_id} created successfully")

    def get_purchase_orders(self):
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
            return f"Invalid transition: {current_status} to {status}"

        updated = self.repo.update_po_status(po_id, status)
        if not updated:
            return "Purchase Order not updated"

        self.write_audit(f"Purchase order {po_id} updated successfully by {user}")
        return f"Purchase order {po_id} updated successfully"

    def write_audit(self, message):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(AUDIT_FILE, "a", encoding="utf-8") as file:
            file.write(f"{timestamp} {message}\n")

    def _add_to_budget_spent(self, budget_service, amount):
        if budget_service is None:
            return

        try:
            month_key = budget_service.budget_repo.current_month_key()
            saved_month, saved_budget, saved_spent = budget_service.budget_repo.load_budget_record()

            if saved_month is None or saved_budget is None:
                return

            if saved_month != month_key:
                return

            if saved_spent is None:
                saved_spent = 0.0

            new_spent = float(saved_spent) + float(amount)

            budget_service.budget_repo.save_budget_record(saved_month, saved_budget, new_spent)

        except:
            return
