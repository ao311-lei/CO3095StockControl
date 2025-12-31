from model.purchase_order import PurchaseOrder, PurchaseOrderLine

PO_FILE = "purchase_orders.txt"

class PurchaseOrderRepo:

    def update_po_status(self,po_id,new_status):
        try:
            with open(PO_FILE,"r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            return False

        updated = False
        new_lines = []

        for line in lines:
            parts = line.strip().split("|")

            if len(parts) == 5 and parts[0] == po_id and parts[4] == "HEADER":
                parts[3] = new_status
                new_lines.append("|".join(parts)+"\n")
                updated = True
            else:
                new_lines.append(line)
        if updated:
            with open(PO_FILE,"w") as file:
                file.writelines(new_lines)
        return updated

    def get_po_status(self,po_id):
        try:
            with open(PO_FILE,"r") as file:
                for line in file:
                    parts = line.strip().split("|")
                    if len(parts) == 5 and parts[0] == po_id and parts[4] == "HEADER":
                        return parts[3]
        except FileNotFoundError:
            pass
        return None

    def save_purchase_order(self, purchase_order,lines):
        with open(PO_FILE,"a") as file:
            file.write(
                f"{purchase_order.po_id}|"
                f"{purchase_order.expected_date}|"
                f"{purchase_order.created_by}|"
                f"{purchase_order.status}|HEADER\n")

            for line in lines:
                file.write(
                    f"{line.po_id}|{line.sku}|{line.quantity}\n"
                )

    def get_purchase_orders(self):
        orders = []
        try:
            with open(PO_FILE,"r") as file:
                for line in file:
                    parts= line.strip().split("|")
                    if len(parts) == 5 and parts[4] == "HEADER":
                        orders.append(PurchaseOrder(
                            parts[0], parts[1], parts[2], parts[3]
                        ))
        except FileNotFoundError:
            pass
        return orders
