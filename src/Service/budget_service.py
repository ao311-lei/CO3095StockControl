from Repo.budget_repo import BudgetRepo

class BudgetService:
    def __init__(self, budget_repo: BudgetRepo):
        self.budget_repo = budget_repo

    def _check_current_month(self):
        current_month = self.budget_repo.current_month_key()

        record = self.budget_repo.load_budget_record()

        saved_month = None
        saved_budget = None
        saved_spent = 0.0

        if record is None:
            return current_month, None, 0.0

        if isinstance(record, (list, tuple)):
            if len(record) == 2:
                saved_month, saved_budget = record
                saved_spent = 0.0
            elif len(record) >= 3:
                saved_month, saved_budget, saved_spent = record[0], record[1], record[2]
            else:
                return current_month, None, 0.0
        else:
            return current_month, None, 0.0

        if saved_month is None or saved_budget in [None, ""]:
            return current_month, None, 0.0

        if saved_month != current_month:

            try:
                self.budget_repo.save_budget_record(current_month, "", 0.0)
            except TypeError:
                self.budget_repo.save_budget_record(current_month, "")
            return current_month, None, 0.0

        try:
            saved_budget = float(saved_budget)
        except:
            saved_budget = None

        try:
            saved_spent = float(saved_spent)
        except:
            saved_spent = 0.0

        return saved_month, saved_budget, saved_spent

    def view_monthly_budget(self):
        month_key, budget, spent = self._check_current_month()

        if budget is None:
            return f"No budget set for {month_key} yet."
        remaining = budget - spent
        return (
            f"Monthly budget for {month_key}: £{budget:.2f}\n"
            f"Spent so far: £{spent:.2f}\n"
            f"Remaining: £{remaining:.2f}"
        )

    def set_monthly_budget(self, budget):
        budget = (budget or "").strip()
        if budget == "":
            return "Budget cannot be empty."

        try:
            budget = float(budget)
        except:
            return "Budget must be a number."

        if budget < 0:
            return "Budget cannot be negative."

        month_key, _, spent = self._check_current_month()

        try:
            self.budget_repo.save_budget_record(month_key, budget, spent)
        except TypeError:
            self.budget_repo.save_budget_record(month_key, budget)

        return f"Monthly budget saved for {month_key}: £{budget:.2f}"

    def get_budget_remaining(self):
        month_key, budget, spent = self._check_current_month()
        if budget is None:
            return None  # means "no budget set"
        return budget - spent

    def add_spend(self, amount):
        month_key, budget, spent = self._check_current_month()
        spent = float(spent)

        spent += float(budget)
        self.budget_repo.save_budget_record(month_key, budget, spent)