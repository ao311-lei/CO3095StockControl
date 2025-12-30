from Repo.budget_repo import BudgetRepo

class BudgetService:
    def __init__(self, budget_repo: BudgetRepo, auth_service):
        self.budget_repo = budget_repo
        self.auth_service = auth_service

    def _get_username(self):
        if self.auth_service is None:
            return None
        if self.auth_service.current_user is None:
            return None
        return self.auth_service.current_user.username

    def view_budget(self):
        username = self._get_username()
        if username is None:
            return "You must be logged in to view your budget."

        budget = self.budget_repo.get_budget_for_user(username)
        if budget is None:
            return "No budget set yet for your account."
        return f"Your inventory budget: £{budget:.2f}"

    def set_budget(self, amount_str):
        username = self._get_username()
        if username is None:
            return "You must be logged in to set your budget."

        amount_str = (amount_str or "").strip()
        if amount_str == "":
            return "Budget cannot be empty."

        try:
            amount = float(amount_str)
        except:
            return "Budget must be a number."

        if amount < 0:
            return "Budget cannot be negative."

        self.budget_repo.set_budget_for_user(username, amount)
        return f"Budget saved for {username}: £{amount:.2f}"
