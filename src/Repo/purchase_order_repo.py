from model.purchase_order import PurchaseOrder, PurchaseOrderLine

PO_FILE = "purchase_orders.txt"

class PurchaseOrderRepo:
    def save_purchase_order(self, purchase_order,lines):
        with open(PO_FILE,"a") as file:
            file.write(
                f"{purchase_order.po_id}|"
                f"{purchase_order.expected_date}|"
                f"{purchase_order.created_by}|"
                f"{purchase_order.status}|")

            for line in lines:
                file.write(
                    f"{line.po_id}|{line.sku}|{line.quantity}\n"
                )

    def get_purchase_orders(self):
        orders = []

        try:
            with open(PO_FILE,"r") as file:
                for line in file:
                    parts= line.split("|")
                    if len(parts) == 5:
                        orders.append(PurchaseOrder(
                            parts[0], parts[1], parts[2], parts[3], parts[4]
                        ))
        except FileNotFoundError:
            pass

        return orders
