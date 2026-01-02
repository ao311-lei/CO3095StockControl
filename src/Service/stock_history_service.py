from datetime import datetime, timezone
from Repo.stock_history_repo import StockHistoryRepo
from model.stock_history_entry import StockHistoryEntry


class StockHistoryService:
    def __init__(self, history_repo: StockHistoryRepo):
        self.history_repo = history_repo

    def record(self, sku, delta, new_quantity, action):
        if sku is None or str(sku).strip() == "":
            raise ValueError("Invalid SKU")

        if action is None or str(action).strip() == "":
            raise ValueError("Invalid action")

        delta = int(delta)
        new_quantity = int(new_quantity)

        if new_quantity < 0:
            raise ValueError("Invalid quantity")

        timestamp = datetime.now(timezone.utc).isoformat()
        entry = StockHistoryEntry(str(sku).strip(), delta, new_quantity, str(action).strip(), timestamp)
        return self.history_repo.add_entry(entry)

    def get_history(self, sku=None):
        if sku is None:
            return self.history_repo.get_all()

        sku = str(sku).strip()
        if sku == "":
            raise ValueError("Invalid SKU")

        return self.history_repo.get_by_sku(sku)
