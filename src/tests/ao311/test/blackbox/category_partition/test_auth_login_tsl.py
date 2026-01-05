"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: AuthService.login
TSL spec: specs/auth_login.tsl
"""

import unittest
from Service.auth_service import AuthService
from model.user import User


class FakeUserRepo:
    def __init__(self):
        self.users = {}

    def get_user(self, username):
        return self.users.get(username)

    def save_user(self, user):
        self.users[user.username] = user


class TestAuthLoginTSL(unittest.TestCase):
    def setUp(self):
        self.repo = FakeUserRepo()
        self.auth = AuthService(self.repo)

        # Store a user with correct hashed password (use AuthService hashing)
        hashed = self.auth._hash_password("password123")
        self.repo.save_user(User("alice", hashed, "STAFF"))

        # Avoid writing to real file during tests
        self.auth.write_audit = lambda msg: None

    def test_user_not_found_false(self):
        # Frame: UserExists=No
        self.assertFalse(self.auth.login("missing", "password123"))

    def test_bad_password_false(self):
        # Frame: UserExists=Yes, PasswordCorrect=No
        self.assertFalse(self.auth.login("alice", "wrongpass"))

    def test_correct_password_true(self):
        # Frame: UserExists=Yes, PasswordCorrect=Yes
        self.assertTrue(self.auth.login("alice", "password123"))
        self.assertIsNotNone(self.auth.current_user)


if __name__ == "__main__":
    unittest.main()
