import unittest

from Service.audit_log_service import AuditLogService


class TestAuditLogBranch(unittest.TestCase):
    def setUp(self):
        self.service = AuditLogService()

    # Working input
    def test_record_creates_entry(self):
        self.service.record("admin", "LOGIN", "ok")
        self.assertEqual(len(self.service.get_all()), 1)

    # Working input (format should return strings)
    def test_format_entries(self):
        self.service.record("admin", "LOGIN", "ok")
        formatted = self.service.format_entries()
        self.assertEqual(len(formatted), 1)
