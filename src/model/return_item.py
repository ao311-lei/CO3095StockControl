class ReturnItem:
    def __init__(self, return_id, sku, quantity, condition, decision, reason):
        self.return_id = return_id
        self.sku = sku
        self.quantity = quantity
        self.condition = condition
        self.decision = decision      # "ADDED_TO_STOCK" or "REJECTED"
        self.reason = reason          # text explanation
