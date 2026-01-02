class StockHistoryEntry:
    def __init__(self, sku, delta, new_quantity, action, timestamp):
        self.sku = sku
        self.delta = int(delta)
        self.new_quantity = int(new_quantity)
        self.action = action
        self.timestamp = timestamp

    def to_line(self):
        return f"{self.sku},{self.delta},{self.new_quantity},{self.action},{self.timestamp}"

    @staticmethod
    def from_line(line):
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) < 5:
            return None
        sku = parts[0]
        delta = int(parts[1])
        new_quantity = int(parts[2])
        action = parts[3]
        timestamp = ",".join(parts[4:])
        return StockHistoryEntry(sku, delta, new_quantity, action, timestamp)
