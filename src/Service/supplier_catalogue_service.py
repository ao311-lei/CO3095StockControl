class SupplierCatalogueService:
    def __init__(self, supplier_repo, product_repo, supplier_product_repo):
        self.supplier_repo = supplier_repo
        self.product_repo = product_repo
        self.supplier_product_repo = supplier_product_repo

    def link_product_to_supplier(self, supplier_id, sku):
        supplier_id = (supplier_id or "").strip()
        sku = (sku or "").strip()

        if supplier_id == "" or sku == "":
            return "Supplier ID and SKU cannot be empty."

        supplier = self.supplier_repo.find_by_id(supplier_id)
        if supplier is None:
            return "Supplier not found."
        if supplier.active is False:
            return "Supplier is INACTIVE. Cannot link products."

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            return "Product not found."
        if getattr(product, "active", True) is False:
            return "Product is INACTIVE. Cannot link to supplier."

        added = self.supplier_product_repo.add_link(supplier_id, sku)
        if not added:
            return "This supplier is already linked to that product."

        return "Product linked to supplier successfully."

    def unlink_product_from_supplier(self, supplier_id, sku):
        supplier_id = (supplier_id or "").strip()
        sku = (sku or "").strip()

        if supplier_id == "" or sku == "":
            return "Supplier ID and SKU cannot be empty."

        removed = self.supplier_product_repo.remove_link(supplier_id, sku)
        if removed:
            return "Link removed successfully."
        return "That link does not exist."

    def view_supplier_catalogue(self, supplier_id):
        supplier_id = (supplier_id or "").strip()
        if supplier_id == "":
            return None, "Supplier ID cannot be empty."

        supplier = self.supplier_repo.find_by_id(supplier_id)
        if supplier is None:
            return None, "Supplier not found."

        skus = self.supplier_product_repo.get_products_for_supplier(supplier_id)
        products = []

        for sku in skus:
            p = self.product_repo.find_by_sku(sku)
            if p is not None:
                products.append(p)

        return products, None
