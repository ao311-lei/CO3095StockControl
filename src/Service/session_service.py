from datetime import datetime, timedelta, timezone


class SessionService:
    TIMEOUT_MINUTES = 5

    def __init__(self):
        self.active = False
        self.last_activity = None

    def start_session(self):
        self.active = True
        self.last_activity = datetime.now(timezone.utc)

    def end_session(self):
        self.active = False
        self.last_activity = None

    def touch(self):
        if not self.active:
            raise RuntimeError("No active session")
        self.last_activity = datetime.now(timezone.utc)

    def is_expired(self):
        if not self.active or self.last_activity is None:
            return True
        return datetime.now(timezone.utc) - self.last_activity > timedelta(minutes=self.TIMEOUT_MINUTES)

    def require_active_session(self):
        if self.is_expired():
            self.end_session()
            raise RuntimeError("Session expired. Please log in.")
