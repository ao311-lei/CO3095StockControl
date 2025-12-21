from Repo.product_repo import ProductRepo


class StockService:
    def __init__(self, product_repo: ProductRepo):
        self.product_repo = product_repo

    def record_stock_increase(self, sku, amount):
        pass

    def record_stock_decrease(self, sku, amount):
        pass
