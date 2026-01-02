from collections import Counter, defaultdict
from datetime import datetime, timedelta

AUDIT_FILE = "audit_log.txt"


class ActivityService:
    def __init__(self, filename=AUDIT_FILE):
        self.filename = filename

    def _parse_line(self, line):
        try:
            timestamp_str, message = line.split(" - ", 1)
            timestamp = datetime.strptime(
                timestamp_str.strip(), "%Y-%m-%d %H:%M:%S"
            )
            return timestamp, message.strip()
        except:
            return None, None

    def get_stats(self, hours=24):
        cutoff = datetime.now() - timedelta(hours=hours)

        total_by_user = Counter()
        total_by_action = Counter()
        actions_by_user = defaultdict(Counter)
        failed_logins_by_user = Counter()

        try:
            with open(self.filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line == "":
                        continue

                    timestamp, message = self._parse_line(line)
                    if timestamp is None or timestamp < cutoff:
                        continue

                    user = None
                    action = None

                    parts = message.split()
                    for part in parts:
                        if part.startswith("USER="):
                            user = part.split("=", 1)[1]
                        elif part.startswith("ACTION="):
                            action = part.split("=", 1)[1]

                    if user is None or action is None:
                        continue

                    total_by_user[user] += 1
                    total_by_action[action] += 1
                    actions_by_user[user][action] += 1

                    if action == "LOGIN" and "FAIL" in message:
                        failed_logins_by_user[user] += 1

        except FileNotFoundError:
            pass

        return {
            "total_by_user": total_by_user,
            "total_by_action": total_by_action,
            "actions_by_user": actions_by_user,
            "failed_logins_by_user": failed_logins_by_user,
        }
