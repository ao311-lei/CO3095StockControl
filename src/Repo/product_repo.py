from model.product import Product


class ProductRepo:
    def __init__(self):
        self.products = []

    def add_product(self, product: Product):
        pass

    def get_product(self, sku):
        pass

    def remove_product(self, sku):
        pass

    def update_product(self, sku, **updates):
        pass

    def get_all_products(self):
        pass
