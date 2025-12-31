from model.supplier import Supplier

class SupplierService:
    def __init__(self, supplier_repo):
        self.supplier_repo = supplier_repo

    def _validate_id(self, supplier_id):
        supplier_id = (supplier_id or "").strip()
        if supplier_id == "":
            return None, "Supplier ID cannot be empty"
        return supplier_id, None

    def _validate_name(self, name):
        name = (name or "").strip()
        if name == "":
            return None, "Supplier name cannot be empty"
        return name, None

    def create_supplier(self, supplier_id, name, phone="", email=""):
        supplier_id, err = self._validate_id(supplier_id)
        if err: return err

        name, err = self._validate_name(name)
        if err: return err

        if self.supplier_repo.find_by_id(supplier_id) is not None:
            return "Supplier ID already exists"

        supplier = Supplier(supplier_id, name, phone.strip(), email.strip(), active=True)
        self.supplier_repo.add_supplier(supplier)
        return "Supplier created successfully"

    def update_supplier(self, supplier_id, name, phone="", email=""):
        supplier_id, err = self._validate_id(supplier_id)
        if err: return err

        existing = self.supplier_repo.find_by_id(supplier_id)
        if existing is None:
            return "Supplier not found"

        name = name.strip()
        if name != "":
            existing.name = name

        if phone.strip() != "":
            existing.phone = phone.strip()

        if email.strip() != "":
            existing.email = email.strip()

        self.supplier_repo.update_supplier(existing)
        return "Supplier updated successfully"

    def deactivate_supplier(self, supplier_id):
        supplier_id, err = self._validate_id(supplier_id)
        if err: return err

        s = self.supplier_repo.find_by_id(supplier_id)
        if s is None:
            return "Supplier not found"

        if s.active is False:
            return "Supplier is already INACTIVE"

        s.active = False
        self.supplier_repo.update_supplier(s)
        return "Supplier deactivated successfully"

    def list_suppliers(self):
        return self.supplier_repo.get_all()
