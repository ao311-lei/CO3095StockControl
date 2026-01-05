import unittest

from Service.audit_log_service import AuditLogService


class TestAuditLogSymbolic(unittest.TestCase):
    def setUp(self):
        self.log = AuditLogService()

    # Working input where record adds entry)
    def test_path_record(self):
        self.log.record("user", "ACTION", "details")
        self.assertEqual(len(self.log.get_all()), 1)

    # Working output
    def test_path_format(self):
        self.log.record("user", "ACTION", "details")
        formatted = self.log.format_entries()
        self.assertTrue(isinstance(formatted[0], str))
