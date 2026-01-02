from model.product import Product


class ProductRepo:
    def __init__(self, filename="src/data/products.txt"):
        self.filename = filename
        self.products = []
        self.load_products()

    def load_products(self):
        self.products = []  # reset to avoid duplicates

        try:
            with open(self.filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line == "":
                        continue

                    parts = line.split(",")

                    sku = parts[0].strip()
                    name = parts[1].strip()
                    description = parts[2].strip()
                    quantity = int(parts[3].strip())
                    price = float(parts[4].strip())

                    category = parts[5].strip() if len(parts) > 5 and parts[5].strip() else None
                    active = parts[6].strip().upper() == "ACTIVE" if len(parts) > 6 else True

                    self.products.append(Product(sku, name, description, quantity, price, category, active))

        except FileNotFoundError:
            pass  # file doesn't exist yet -> start empty

    def save_products(self):
        with open(self.filename, "w") as file:
            for product in self.products:
                category = product.category if product.category is not None else ""
                status = "ACTIVE" if getattr(product, "active", True) else "INACTIVE"

                line = (
                    f"{product.sku},{product.name},{product.description},"
                    f"{product.quantity},{product.price},{category},{status}"
                )
                file.write(line + "\n")

    def add_product(self, product: Product):
        self.products.append(product)
        self.save_products()

    def remove_by_sku(self, sku):
        for i in range(len(self.products)):
            if self.products[i].sku == sku:
                del self.products[i]
                self.save_products()
                return True
        return False

    def update_product(self, sku, name, description, quantity, price, category):
        p = self.find_by_sku(sku)
        if p is None:
            return False

        p.name = name
        p.description = description
        p.quantity = quantity
        p.price = price
        p.category = category

        self.save_products()
        return True

    def find_by_sku(self, sku):
        for product in self.products:
            if product.sku == sku:
                return product
        return None

    def save_product(self, product: Product):
        for i in range(len(self.products)):
            if self.products[i].sku == product.sku:
                self.products[i] = product
                self.save_products()
                return True
        return False

    def get_product_quantity(self, sku):
        p = self.find_by_sku(sku)
        if p is None:
            return None
        return int(p.quantity)

    def product_active(self, sku):
        # Uses in-memory products (simpler + consistent)
        p = self.find_by_sku(sku)
        if p is None:
            return False
        return getattr(p, "active", True)

    def get_all_products(self):
        return self.products
