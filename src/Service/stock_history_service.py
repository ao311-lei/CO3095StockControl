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

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        entry = StockHistoryEntry(str(sku).strip(), delta, new_quantity, str(action).strip(), timestamp)
        return self.history_repo.add_entry(entry)

    def get_history(self, sku=None):
        if sku is None:
            return self.history_repo.get_all()

        sku = str(sku).strip()
        if sku == "":
            raise ValueError("Invalid SKU")

        return self.history_repo.get_by_sku(sku)

    def view_history(self, sku=None, limit=None):
        entries = self.get_history(sku)
        entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)

        if limit is not None:
            limit = int(limit)
            if limit < 1:
                raise ValueError("Invalid limit")
            entries = entries[:limit]

        return [
            {
                "sku": e.sku,
                "delta": e.delta,
                "new_quantity": e.new_quantity,
                "action": e.action,
                "timestamp": e.timestamp
            }
            for e in entries
        ]

    def view_history_lines(self, sku=None, limit=None):
        rows = self.view_history(sku=sku, limit=limit)
        return [
            f"{r['timestamp']} | {r['sku']} | {r['action']} | {r['delta']} | new={r['new_quantity']}"
            for r in rows
        ]

