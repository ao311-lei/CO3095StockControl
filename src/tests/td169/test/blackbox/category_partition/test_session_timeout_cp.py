import unittest
from datetime import datetime, timedelta, timezone

from Service.session_service import SessionService


class TestSessionTimeoutCP(unittest.TestCase):
    def test_new_session_not_expired(self):
        s = SessionService()
        s.active = True
        s.last_activity = datetime.now(timezone.utc)
        self.assertFalse(s.is_expired())

    def test_expired_after_timeout(self):
        s = SessionService()
        s.active = True
        s.last_activity = datetime.now(timezone.utc) - timedelta(minutes=6)
        self.assertTrue(s.is_expired())

    def test_inactive_session_expired(self):
        s = SessionService()
        s.active = False
        s.last_activity = datetime.now(timezone.utc)
        self.assertTrue(s.is_expired())

    def test_no_last_activity_expired(self):
        s = SessionService()
        s.active = True
        s.last_activity = None
        self.assertTrue(s.is_expired())

    def test_touch_prevents_expiry(self):
        s = SessionService()
        s.active = True
        s.last_activity = datetime.now(timezone.utc) - timedelta(minutes=6)
        self.assertTrue(s.is_expired())
        s.touch()
        self.assertFalse(s.is_expired())
