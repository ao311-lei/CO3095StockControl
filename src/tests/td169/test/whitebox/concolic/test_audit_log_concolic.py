import unittest

from Service.audit_log_service import AuditLogService


class TestAuditLogConcolic(unittest.TestCase):
    def setUp(self):
        self.service = AuditLogService()

    # Working inputs for multiple
    def test_concolic_record_cases(self):
        cases = [
            ("admin", "LOGIN", "ok"),
            ("staff", "STOCK_INCREASE", "SKU1 +5"),
            ("admin", "VIEW_AUDIT", ""),
        ]
        for user, action, details in cases:
            with self.subTest(user=user, action=action):
                self.service.record(user, action, details)

        self.assertEqual(len(self.service.get_all()), 3)

    # Working output
    def test_concolic_format_cases(self):
        self.service.record("admin", "LOGIN", "ok")
        self.service.record("admin", "LOGOUT", "bye")
        formatted = self.service.format_entries()
        self.assertEqual(len(formatted), 2)
