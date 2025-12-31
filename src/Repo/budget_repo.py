from datetime import date

class BudgetRepo:
    def __init__(self, filename="budgets.txt"):
        self.filename = filename
        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def load_budget_record(self):

        try:
            with open(self.filename, "r") as file:
                line = file.read().strip()

                if line == "":
                    return None, None  # month_key, amount

                parts = line.split(",", 1)
                if len(parts) != 2:
                    return None, None

                month_key = parts[0].strip()
                amount = float(parts[1].strip())

                if amount == "":
                    return month_key, None

                return month_key, float(amount)
        except:
            return None, None

    def save_budget_record(self, month_key, amount):
        with open(self.filename, "w") as file:
            file.write(f"{month_key},{amount}")

    def current_month_key(self):
        today = date.today()
        return f"{today.year:04d}-{today.month:02d}"
