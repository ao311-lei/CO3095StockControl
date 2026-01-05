from pathlib import Path
from model.stock_history_entry import StockHistoryEntry


class StockHistoryRepo:
    def __init__(self, filename="src/data/stock_history.txt"):
        project_root = Path(__file__).resolve().parents[2]
        self.filepath = project_root / filename
        self.entries = []
        self.load()

    def load(self):
        self.entries = []
        if not self.filepath.exists():
            return
        for line in self.filepath.read_text(encoding="utf-8").splitlines():
            entry = StockHistoryEntry.from_line(line)
            if entry is not None:
                self.entries.append(entry)

    def add_entry(self, entry: StockHistoryEntry):
        self.entries.append(entry)
        with self.filepath.open("w", encoding="utf-8") as f:
            for e in self.entries:
                f.write(e.to_line() + "\n")
        return entry

    def get_all(self):
        return self.entries

    def get_by_sku(self, sku):
        return [e for e in self.entries if e.sku == sku]
