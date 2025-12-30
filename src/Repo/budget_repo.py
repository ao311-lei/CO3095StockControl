class BudgetRepo:
    def __init__(self, filename="budgets.txt"):
        self.filename = filename
        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def load_all(self):
        budgets = {}  # username -> float
        with open(self.filename, "r") as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue

                parts = line.split(",", 1)
                if len(parts) != 2:
                    continue

                username = parts[0].strip()
                amount_str = parts[1].strip()

                try:
                    budgets[username] = float(amount_str)
                except:
                    continue

        return budgets

    def save_all(self, budgets):
        with open(self.filename, "w") as file:
            for username, amount in budgets.items():
                file.write(f"{username},{amount}\n")

    def get_budget_for_user(self, username):
        budgets = self.load_all()
        return budgets.get(username)

    def set_budget_for_user(self, username, amount):
        budgets = self.load_all()
        budgets[username] = amount
        self.save_all(budgets)
