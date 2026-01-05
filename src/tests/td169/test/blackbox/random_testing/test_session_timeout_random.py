import random
import unittest
from datetime import timedelta

from Service.session_service import SessionService


class TestSessionTimeoutRandom(unittest.TestCase):
    def setUp(self):
        random.seed(7)
        self.session = SessionService(timeout_minutes=5)

    def test_start_session_sets_active(self):
        self.session.start_session("user1")
        self.assertTrue(self.session.is_active())
        self.assertEqual(self.session.current_user, "user1")

    def test_touch_keeps_session_active(self):
        self.session.start_session("user1")
        for i in range(5):
            with self.subTest(i=i):
                self.session.touch()
                self.assertTrue(self.session.is_active())

    def test_expired_session_blocks_actions(self):
        self.session.start_session("user1")
        self.session.last_activity = self.session.last_activity - timedelta(minutes=6)
        self.assertTrue(self.session.is_expired())
        with self.assertRaises(RuntimeError):
            self.session.require_active_session()

    def test_end_session_invalidates(self):
        self.session.start_session("user1")
        self.session.end_session()
        self.assertFalse(self.session.is_active())
        with self.assertRaises(RuntimeError):
            self.session.require_active_session()
