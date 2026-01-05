import unittest

from Service.audit_log_service import AuditLogService


class TestAuditLogCP(unittest.TestCase):
    def setUp(self):
        self.service = AuditLogService()

    def test_record_adds_entry(self):
        self.service.record("admin", "ACTION", "details")
        entries = self.service.get_all()
        self.assertEqual(len(entries), 1)

    def test_entry_fields_exist(self):
        self.service.record("user1", "DELETE_PRODUCT", "SKU=SKU1")
        entry = self.service.get_all()[0]
        self.assertIn("timestamp", entry)
        self.assertIn("user", entry)
        self.assertIn("action", entry)
        self.assertIn("details", entry)

    def test_multiple_entries_appended(self):
        self.service.record("u1", "A1", "")
        self.service.record("u2", "A2", "x")
        self.assertEqual(len(self.service.get_all()), 2)

    def test_get_all_returns_copy(self):
        self.service.record("u1", "A1", "")
        entries = self.service.get_all()
        entries.append({"fake": True})
        self.assertEqual(len(self.service.get_all()), 1)

    def test_format_entries_returns_strings(self):
        self.service.record("u1", "A1", "d")
        formatted = self.service.format_entries()
        self.assertTrue(all(isinstance(x, str) for x in formatted))
        self.assertEqual(len(formatted), 1)
