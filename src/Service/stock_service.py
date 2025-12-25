from Repo.product_repo import ProductRepo


class StockService:
    def __init__(self, product_repo: ProductRepo):
        self.product_repo = product_repo

    def record_stock_increase(self, sku, amount):
        pass

    def record_stock_decrease(self, sku, amount):
        if amount <= 0:
            raise ValueError("Decrease amount must be a positive integer")

        product = self.product_repo.get_by_sku(sku)
        if product is None:
            raise ValueError("Invalid SKU")

        if product.stock < amount:
            raise ValueError("Insufficient sotck")

        product.stock -= amount
        self.product_repo.update(product)
        return product.stock
