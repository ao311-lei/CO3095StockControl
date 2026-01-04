class ConfirmService:
    def __init__(self, confirmer=None):
        self.confirmer = confirmer or self._default_confirmer

    def _default_confirmer(self, message):
        answer = input(f"{message} (yes/no): ").strip().lower()
        return answer in ("y", "yes")

    def require_confirm(self, message):
        if not self.confirmer(message):
            raise PermissionError("Cancelled")
