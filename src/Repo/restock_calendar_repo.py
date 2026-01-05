from pathlib import Path
from model.restock_rule import RestockRule


class RestockCalendarRepo:
    def __init__(self, filename="restock_rules.txt"):
        project_root = Path(__file__).resolve().parents[2]
        self.filepath = project_root / filename
        self.rules = {}
        self.load()

    def load(self):
        self.rules = {}
        if not self.filepath.exists():
            return
        for line in self.filepath.read_text(encoding="utf-8").splitlines():
            rule = RestockRule.from_line(line)
            if rule is not None:
                self.rules[rule.sku] = rule

    def save(self):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        lines = [r.to_line() for r in self.rules.values()]
        self.filepath.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    def set_rule(self, sku, reorder_level, lead_time_days):
        rule = RestockRule(sku, reorder_level, lead_time_days)
        self.rules[sku] = rule
        self.save()
        return rule

    def get_rule(self, sku):
        return self.rules.get(sku)

    def get_all_rules(self):
        return list(self.rules.values())

    def remove_rule(self, sku):
        if sku in self.rules:
            del self.rules[sku]
            self.save()
            return True
        return False
