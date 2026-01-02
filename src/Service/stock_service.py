from Repo.product_repo import ProductRepo

AUDIT_FILE = "audit_log.txt"


class StockService:
    def __init__(self, product_repo: ProductRepo):
        self.product_repo = product_repo

    def record_stock_increase(self, sku, amount,user=None):
        if amount <= 0:
            raise ValueError("Increase amount must be a positive integer")

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            raise ValueError("Invalid SKU")

        if getattr(product, "active", True) is False:
            raise ValueError("This product is INACTIVE and cannot be used in stock operations.")

        product.quantity += amount
        self.product_repo.save_products()
        return product.quantity

    def record_stock_decrease(self, sku, amount):
        if amount <= 0:
            raise ValueError("Decrease amount must be a positive integer")

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            raise ValueError("Invalid SKU")

        if getattr(product, "active", True) is False:
            raise ValueError("This product is INACTIVE and cannot be used in stock operations.")

        if product.quantity < amount:
            raise ValueError("Insufficient stock")

        product.quantity -= amount
        self.product_repo.save_products()
        write_audit(f"USER={user} ACTION=STOCK_DECREASE sku={sku} amount={amount} new_qty={product.quantity}")
        return product.quantity
