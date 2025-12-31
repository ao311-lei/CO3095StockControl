from Repo.budget_repo import BudgetRepo

class BudgetService:
    def __init__(self, budget_repo: BudgetRepo):
        self.budget_repo = budget_repo

    def _check_current_month(self):

        current_month = self.budget_repo.current_month_key()
        saved_month, saved_amount = self.budget_repo.load_budget_record()

        if saved_month is None or saved_amount is None:
            return current_month, None

        if saved_month != current_month:
            self.budget_repo.save_budget_record(current_month, "")
            return current_month, None

        return saved_month, saved_amount

    def view_monthly_budget(self):
        month_key, amount = self._check_current_month()

        if amount is None:
            return f"No budget set for {month_key} yet."
        return f"Monthly budget for {month_key}: £{amount:.2f}"

    def set_monthly_budget(self, amount):
        amount = (amount or "").strip()
        if amount == "":
            return "Budget cannot be empty."

        try:
            amount = float(amount)
        except:
            return "Budget must be a number."

        if amount < 0:
            return "Budget cannot be negative."

        month_key = self.budget_repo.current_month_key()
        self.budget_repo.save_budget_record(month_key, amount)
        return f"Monthly budget saved for {month_key}: £{amount:.2f}"
