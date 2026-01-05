from datetime import date, timedelta


class RestockCalendarService:
    def __init__(self, product_repo):
        self.product_repo = product_repo
        self.restock_rules = {}

    def set_restock_rule(self, sku, reorder_level, lead_time_days):
        if sku is None or str(sku).strip() == "":
            raise ValueError("Invalid SKU")

        reorder_level = int(reorder_level)
        lead_time_days = int(lead_time_days)

        if reorder_level < 0 or lead_time_days < 0:
            raise ValueError("Invalid restock rule")

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            raise ValueError("Product not found")

        self.restock_rules[sku] = {
            "reorder_level": reorder_level,
            "lead_time_days": lead_time_days
        }

        return self.restock_rules[sku]

    def get_restock_calendar(self):
        today = date.today()
        calendar = []

        for product in self.product_repo.get_all_products():
            rule = self.restock_rules.get(product.sku)
            if rule is None:
                continue

            if product.quantity >= rule["reorder_level"]:
                due_date = today + timedelta(days=rule["lead_time_days"])
                calendar.apend({
                    "sku": product.sku,
                    "quantity": product.quantity,
                    "reorder_level": rule["reorder_level"],
                    "restock_due_date": due_date.isoformat()
                })

        calendar.sort(key=lambda x: x["restock_due_date"])
        return calendar
