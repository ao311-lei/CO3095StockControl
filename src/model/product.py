from unicodedata import category


class Product:
    def __init__(self,sku, name, description,quantity, price, category):
        self.sku = sku
        self.name = name
        self.description = description
        self.quantity = quantity
        self.price = price
        self.category = category

    def __str__(self):
        return self.sku + " | " + self.name + " | " + str(self.quantity) + " | £" + str(self.price)
g