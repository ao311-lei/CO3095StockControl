from Repo.product_repo import ProductRepo
from Repo.category_repo import CategoryRepo


class ProductService:
    def __init__(self, product_repo: ProductRepo, category_repo: CategoryRepo):
        self.product_repo = product_repo
        self.category_repo = category_repo

    def add_new_product(self, sku, name, description, quantity, price, category=None):
        pass

    def update_product(self, sku, **updates):
        pass

    def remove_product(self, sku):
        pass

    def search_products(self, query):
        pass

    def filter_by_category(self, category_name):
        pass
