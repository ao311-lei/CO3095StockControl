import unittest
from Service.audit_log_service import AuditLogService


class TestAuditLogStatement(unittest.TestCase):

    # Record entry
    def test_record(self):
        log = AuditLogService()
        log.record("user", "ACTION", "details")
        self.assertEqual(len(log.get_all()), 1)

    # Format output
    def test_format_entries(self):
        log = AuditLogService()
        log.record("user", "ACTION", "details")
        formatted = log.format_entries()
        self.assertTrue("ACTION" in formatted[0])
