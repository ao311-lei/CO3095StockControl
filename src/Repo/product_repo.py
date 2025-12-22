from unicodedata import category

from model.product import Product


class ProductRepo:
    def __init__(self, filename="products.txt"):
        self.filename = filename
        self.products = []
        self.load_products()

    def load_products(self):
        try:
            file = open(self.filename, "r")
            lines = file.readlines()
            file.close()

            for line in lines:
                line = line.strip()
                if line != "":
                    parts = line.split(",")

                    sku = parts[0]
                    name = parts[1]
                    description = parts[2]
                    quantity = parts[3]
                    price = parts[4]

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

    def find_by_sku(self, sku):
        for product in self.products:
            if product.sku == sku:
                return product
        return None

    def get_product(self, sku):
        pass

    def remove_product(self, sku):
        pass

    def update_product(self, sku, **updates):
        pass

    def get_all_products(self):
        return self.products
