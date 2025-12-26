from unicodedata import category

from model.product import Product


class ProductRepo:
    def __init__(self, filename="products.txt"):
        self.filename = filename
        self.products = []
        self.load_products()

    def load_products(self):
        self.products = []  # reset to avoid duplicates if called again

        try:
            file = open(self.filename, "r")
            lines = file.readlines()
            file.close()

            for line in lines:
                line = line.strip()
                if line != "":
                    parts = line.split(",")

                    sku = parts[0].strip()
                    name = parts[1].strip()
                    description = parts[2].strip()
                    quantity = int(parts[3].strip())
                    price = float(parts[4].strip())

                    category = None
                    if len(parts) > 5 and parts[5] != "":
                        category = parts[5]

                    product = Product(sku, name, description, quantity, price, category)
                    self.products.append(product)

        except FileNotFoundError:
            pass # If the file doesn't exist yet, start with an empty list

    def save_products(self):
        file = open(self.filename, "w")
        for product in self.products:
            category = ""
            if product.category != None:
                category = product.category

            line = (
                    product.sku + "," +
                    product.name + "," +
                    product.description + "," +
                    str(product.quantity) + "," +
                    str(product.price) + "," +
                    category
            )
            file.write(line + "\n")
        file.close()

    def add_product(self, product: Product):
        self.products.append(product)
        self.save_products()

    def remove_by_sku(self, sku):
        # Find index of product with this SKU
        for i in range(len(self.products)):
            if self.products[i].sku == sku:
                del self.products[i]
                self.save_products()  # update products.txt
                return True
        return False

    def update_product(self, sku, name, description, quantity, price, category):
        p = self.find_by_sku(sku)
        if p == None:
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

    def get_product(self, sku):
        pass

    def remove_product(self, sku):
        pass


    def get_all_products(self):
        return self.products
