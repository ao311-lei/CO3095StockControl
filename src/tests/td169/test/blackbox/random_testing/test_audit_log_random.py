import random
import unittest

from Service.audit_log_service import AuditLogService


class TestAuditLogRandom(unittest.TestCase):
    def setUp(self):
        random.seed(99)
        self.audit = AuditLogService()

    def test_record_random_entries_increases_count(self):
        n = 10
        for i in range(n):
            user = random.choice(["admin", "staff", "viewer"])
            action = random.choice(["LOGIN", "LOGOUT", "STOCK_DECREASE", "DELETE_PRODUCT"])
            details = f"details-{random.randint(1, 999)}"
            self.audit.record(user, action, details)

        self.assertEqual(len(self.audit.get_all()), n)

    def test_format_entries_matches_count(self):
        for i in range(5):
            self.audit.record("admin", f"ACTION_{i}", "x")
        formatted = self.audit.format_entries()
        self.assertEqual(len(formatted), 5)

    def test_format_entries_contains_user_and_action(self):
        self.audit.record("admin", "LOGIN", "ok")
        line = self.audit.format_entries()[0]
        self.assertIn("admin", line)
        self.assertIn("LOGIN", line)

    def test_get_all_returns_copy(self):
        self.audit.record("admin", "LOGIN", "ok")
        all1 = self.audit.get_all()
        all1.append({"fake": True})
        all2 = self.audit.get_all()
        self.assertEqual(len(all2), 1)
