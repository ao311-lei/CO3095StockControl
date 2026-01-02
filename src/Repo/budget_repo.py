from datetime import date

class BudgetRepo:
    def __init__(self, filename="src/data/budgets.txt"):
        self.filename = filename
        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def load_budget_record(self):
        try:
            with open(self.filename, "r") as file:
                line = file.readline().strip()
                if not line:
                    return None, None, None

                parts = line.split("|")
                if len(parts) < 2:
                    return None, None, None

                month = parts[0].strip()

                # budget
                budget_str = parts[1].strip()
                budget = None
                if budget_str != "":
                    budget = float(budget_str)

                # spent (optional)
                spent = 0.0
                if len(parts) >= 3 and parts[2].strip() != "":
                    spent = float(parts[2].strip())

                return month, budget, spent
        except FileNotFoundError:
            return None, None, None

    def save_budget_record(self, month_key, budget_amount, spent_amount=0.0):
        budget_text = "" if budget_amount is None else str(budget_amount)
        spent_text = str(spent_amount)

        with open(self.filename, "w") as file:
            file.write(f"{month_key}|{budget_text}|{spent_text}\n")

    def current_month_key(self):
        today = date.today()
        return f"{today.year:04d}-{today.month:02d}"
