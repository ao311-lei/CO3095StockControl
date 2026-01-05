import unittest
from datetime import timedelta

from Service.session_service import SessionService


class TestSessionTimeoutConcolic(unittest.TestCase):
    def setUp(self):
        self.session = SessionService(timeout_minutes=5)

    # Working inputs (session stays valid with touch)
    def test_concolic_active_cases(self):
        self.session.start_session("user1")
        self.session.touch()
        self.assertTrue(self.session.is_active())

    # Invalid inputs (expired session should block)
    def test_concolic_expired_cases(self):
        self.session.start_session("user1")
        self.session.last_activity = self.session.last_activity - timedelta(minutes=6)
        with self.assertRaises(RuntimeError):
            self.session.require_active_session()
