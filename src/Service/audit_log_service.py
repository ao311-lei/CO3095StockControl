from datetime import datetime, timezone


class AuditLogService:
    def __init__(self):
        self.entries = []

    def record(self, user, action, details=""):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "user": user,
            "action": action,
            "details": details
        }
        self.entries.append(entry)

    def get_all(self):
        return list(self.entries)

    def format_entries(self):
        return [
            f"{e['timestamp']} | {e['user']} | {e['action']} | {e['details']}"
            for e in self.entries
        ]

