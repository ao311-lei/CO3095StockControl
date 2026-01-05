import unittest
from datetime import timedelta

from Service.session_service import SessionService


class TestSessionTimeoutSymbolic(unittest.TestCase):
    def setUp(self):
        self.s = SessionService(timeout_minutes=5)

    # Working input (path - active and not expired)
    def test_path_active_not_expired(self):
        self.s.start_session("user1")
        self.s.touch()
        self.assertFalse(self.s.is_expired())

    # Invalid input
    def test_path_expired(self):
        self.s.start_session("user1")
        self.s.last_activity = self.s.last_activity - timedelta(minutes=6)
        with self.assertRaises(RuntimeError):
            self.s.require_active_session()
