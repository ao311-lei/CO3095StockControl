from model.return_item import ReturnItem

class ReturnService:
    # conditions that CAN go back into stock
    ACCEPTED_CONDITIONS = ["sealed", "unopened", "resellable"]

    def __init__(self, product_repo, stock_service, return_repo):
        self.product_repo = product_repo
        self.stock_service = stock_service
        self.return_repo = return_repo
        self._next_id = 1  # simple uni-level ID

    def process_return(self, sku, quantity, condition):
        sku = (sku or "").strip()
        condition = (condition or "").strip().lower()

        # Requirement 1: SKU not empty
        if sku == "":
            return "SKU cannot be empty"

        # Requirement 2: product exists
        product = self.product_repo.find_by_sku(sku)
        if product is None:
            r = ReturnItem(self._next_id, sku, quantity, condition, "REJECTED", "Product not found")
            self._next_id += 1
            self.return_repo.save_return(r)
            return "Return rejected: Product not found"

        # Requirement 3: product active
        if getattr(product, "active", True) is False:
            r = ReturnItem(self._next_id, sku, quantity, condition, "REJECTED", "Product is inactive")
            self._next_id += 1
            self.return_repo.save_return(r)
            return "Return rejected: Product is inactive"

        # Requirement 4: quantity valid (whole number > 0)
        try:
            qty = int(quantity)
        except:
            return "Quantity must be a whole number"

        if qty <= 0:
            return "Quantity must be greater than 0"

        # Requirement 5: condition check
        if condition not in self.ACCEPTED_CONDITIONS:
            # Do NOT add to stock, but still record return
            r = ReturnItem(self._next_id, sku, qty, condition, "REJECTED",
                           "Condition not accepted for restock")
            self._next_id += 1
            self.return_repo.save_return(r)
            return "Return recorded but NOT added to stock (condition not accepted)."

        # If all requirements met -> add to stock
        try:
            new_qty = self.stock_service.record_stock_increase(sku, qty)
        except Exception as e:
            # If stock increase fails for any reason, record rejection
            r = ReturnItem(self._next_id, sku, qty, condition, "REJECTED", str(e))
            self._next_id += 1
            self.return_repo.save_return(r)
            return "Return rejected: " + str(e)

        r = ReturnItem(self._next_id, sku, qty, condition, "ADDED_TO_STOCK", "Added back into stock")
        self._next_id += 1
        self.return_repo.save_return(r)

        return f"Return accepted. Stock updated. New quantity: {new_qty}"
