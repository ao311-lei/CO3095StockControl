from model.supplier import Supplier

class SupplierRepo:
    def __init__(self, filename="src/data/suppliers.txt"):
        self.filename = filename
        self.suppliers = []
        self.load_suppliers()

    def load_suppliers(self):
        self.suppliers = []
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line == "":
                        continue

                    parts = line.split(",")
                    supplier_id = parts[0].strip()
                    name = parts[1].strip()

                    phone = parts[2].strip() if len(parts) > 2 else ""
                    email = parts[3].strip() if len(parts) > 3 else ""
                    status = parts[4].strip().upper() if len(parts) > 4 else "ACTIVE"

                    active = (status == "ACTIVE")
                    self.suppliers.append(Supplier(supplier_id, name, phone, email, active))
        except FileNotFoundError:
            # Create empty file on first run
            open(self.filename, "w").close()

    def save_suppliers(self):
        with open(self.filename, "w") as file:
            for s in self.suppliers:
                status = "ACTIVE" if s.active else "INACTIVE"
                file.write(f"{s.supplier_id},{s.name},{s.phone},{s.email},{status}\n")

    def get_all(self):
        return self.suppliers

    def find_by_id(self, supplier_id):
        for s in self.suppliers:
            if s.supplier_id == supplier_id:
                return s
        return None

    def add_supplier(self, supplier):
        self.suppliers.append(supplier)
        self.save_suppliers()

    def update_supplier(self, supplier):
        for i in range(len(self.suppliers)):
            if self.suppliers[i].supplier_id == supplier.supplier_id:
                self.suppliers[i] = supplier
                self.save_suppliers()
                return True
        return False
