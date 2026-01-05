"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: AuthService.sign_up
TSL spec: specs/auth_signup.tsl
Notes:
- username "" -> ValueError
- password len<8 -> ValueError
- existing username -> ValueError
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


class TestAuthSignUpTSL(unittest.TestCase):
    def setUp(self):
        self.repo = FakeUserRepo()
        self.auth = AuthService(self.repo)
        # Seed an existing user
        self.repo.users["existing"] = User("existing", "hashed", "STAFF")

    def test_username_empty_error(self):
        # Frame: Username=Empty [error]
        with self.assertRaises(ValueError):
            self.auth.sign_up("", "password123", "STAFF")

    def test_username_whitespace_error(self):
        # Frame: Username=WhitespaceOnly [error] -> strip() makes it ""
        with self.assertRaises(ValueError):
            self.auth.sign_up("   ", "password123", "STAFF")

    def test_password_too_short_error(self):
        # Frame: Password=TooShort [error]
        with self.assertRaises(ValueError):
            self.auth.sign_up("newuser", "short7", "STAFF")

    def test_username_existing_error(self):
        # Frame: Username=ValidExisting [error]
        with self.assertRaises(ValueError):
            self.auth.sign_up("existing", "password123", "STAFF")

    def test_valid_new_min_length_ok(self):
        # Frame: Username=ValidNew, Password=MinLength8
        self.assertTrue(self.auth.sign_up("newuser", "password", "STAFF"))
        self.assertIsNotNone(self.repo.get_user("newuser"))

    def test_valid_new_long_password_ok(self):
        # Frame: Username=ValidNew, Password=LongEnough
        self.assertTrue(self.auth.sign_up("newuser2", "password12345", "MANAGER"))
        self.assertEqual(self.repo.get_user("newuser2").role, "MANAGER")

    def test_role_invalid_still_stored_upper(self):
        # Frame: Role=InvalidRole (note: sign_up does NOT validate role)
        self.assertTrue(self.auth.sign_up("newuser3", "password123", "cashier"))
        self.assertEqual(self.repo.get_user("newuser3").role, "CASHIER")


if __name__ == "__main__":
    unittest.main()
