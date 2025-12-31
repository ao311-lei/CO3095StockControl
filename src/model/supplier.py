class Supplier:
    def __init__(self, supplier_id, name, phone="", email="", active=True):
        self.supplier_id = supplier_id
        self.name = name
        self.phone = phone
        self.email = email
        self.active = active

    def __str__(self):
        status = "ACTIVE" if self.active else "INACTIVE"
        return f"{self.supplier_id} | {self.name} | {self.phone} | {self.email} | {status}"
