class SupplierProductRepo:
    def __init__(self, filename="supplier_products.txt"):
        self.filename = filename
        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def load_all_links(self):
        links = []
        with open(self.filename, "r") as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split(",", 1)
                if len(parts) != 2:
                    continue
                supplier_id = parts[0].strip()
                sku = parts[1].strip()
                links.append((supplier_id, sku))
        return links

    def save_all_links(self, links):
        with open(self.filename, "w") as file:
            for supplier_id, sku in links:
                file.write(f"{supplier_id},{sku}\n")

    def add_link(self, supplier_id, sku):
        links = self.load_all_links()
        if (supplier_id, sku) not in links:
            links.append((supplier_id, sku))
            self.save_all_links(links)
            return True
        return False

    def remove_link(self, supplier_id, sku):
        links = self.load_all_links()
        new_links = []
        removed = False

        for s_id, s_sku in links:
            if s_id == supplier_id and s_sku == sku:
                removed = True
            else:
                new_links.append((s_id, s_sku))

        if removed:
            self.save_all_links(new_links)

        return removed

    def get_products_for_supplier(self, supplier_id):
        skus = []
        for s_id, sku in self.load_all_links():
            if s_id == supplier_id:
                skus.append(sku)
        return skus

    def get_suppliers_for_product(self, sku):
        supplier_ids = []
        for s_id, s_sku in self.load_all_links():
            if s_sku == sku:
                supplier_ids.append(s_id)
        return supplier_ids
