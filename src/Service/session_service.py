from datetime import datetime, timedelta, timezone


class SessionService:
    TIMEOUT_MINUTES = 5

    def __init__(self, timeout_minutes=5):
        self.active = False
        self.last_activity = None
        self.timeout = timedelta(minutes=timeout_minutes)
        self.current_user = None



    def start_session(self, user=None):
        self.active = True
        self.last_activity = datetime.now(timezone.utc)
        self.current_user = user


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
        return datetime.now(timezone.utc) - self.last_activity > self.timeout


    def require_active_session(self):
        if self.is_expired():
            self.end_session()
            raise RuntimeError("Session expired. Please log in.")

    def is_active(self):
        if not self.active:
            return False
        return not self.is_expired()

