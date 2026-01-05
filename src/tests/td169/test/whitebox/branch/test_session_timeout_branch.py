import unittest
from datetime import timedelta

from Service.session_service import SessionService


class TestSessionTimeoutBranch(unittest.TestCase):
    def setUp(self):
        self.session = SessionService(timeout_minutes=5)

    # Working input
    def test_active_session_not_expired(self):
        self.session.start_session("user1")
        self.session.touch()
        self.assertFalse(self.session.is_expired())

    # Invalid (expired session)
    def test_expired_session_raises(self):
        self.session.start_session("user1")
        self.session.last_activity = self.session.last_activity - timedelta(minutes=6)
        with self.assertRaises(RuntimeError):
            self.session.require_active_session()
