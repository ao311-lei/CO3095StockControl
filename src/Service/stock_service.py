from Repo.product_repo import ProductRepo


class StockService:
    def __init__(self, product_repo: ProductRepo):
        self.product_repo = product_repo

    def record_stock_increase(self, sku, amount):
        if amount <= 0:
            raise ValueError("Increase amount must be a positive integer")

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            raise ValueError("Invalid SKU")

        product.quantity += amount
        self.product_repo.save_products()
        return product.quantity

    def record_stock_decrease(self, sku, amount):
        if amount <= 0:
            raise ValueError("Decrease amount must be a positive integer")

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            raise ValueError("Invalid SKU")

        if product.stock < amount:
            raise ValueError("Insufficient stock")

        product.stock -= amount
        self.product_repo.save_products()
        return product.quantity
