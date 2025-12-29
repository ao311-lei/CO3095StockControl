from unicodedata import category


class Product:
    def __init__(self,sku, name, description,quantity, price, category, active=True):
        self.sku = sku
        self.name = name
        self.description = description
        self.quantity = quantity
        self.price = price
        self.category = category
        self.active = active

    def status_text(self):
        return "ACTIVE" if self.active else "INACTIVE"

    def __str__(self):
        return self.sku + " | " + self.name + " | " + str(self.quantity) + " | £" + str(self.price) + " | " +self.status_text()

