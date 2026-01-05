import unittest
from Service.session_service import SessionService
import time


class TestSessionTimeoutStatement(unittest.TestCase):

    # Session starts correctly
    def test_start_session(self):
        s = SessionService()
        s.start_session()
        self.assertTrue(s.active)

    # Touch updates activity
    def test_touch_active_session(self):
        s = SessionService()
        s.start_session()
        s.touch()
        self.assertFalse(s.is_expired())

    # Expired session detected
    def test_expired_session(self):
        s = SessionService(timeout_minutes=0)
        s.start_session()
        time.sleep(1)
        self.assertTrue(s.is_expired())

    # No active session
    def test_touch_no_session(self):
        s = SessionService()
        with self.assertRaises(RuntimeError):
            s.touch()
