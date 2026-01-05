import unittest
from Service.auth_service import AuthService
from model.user import User
import os
import tempfile
from Service import auth_service as auth_mod



class FakeUserRepo:
    def __init__(self):
        self.users = {}

    def get_user(self, username):
        return self.users.get(username)

    def save_user(self, user):
        self.users[user.username] = user

    def update_role(self, username, new_role):
        u = self.users.get(username)
        if u is None:
            return False
        u.role = new_role
        return True


class TestAuthServiceBranch(unittest.TestCase):
    """
    CO3095 White-box Branch Testing (Lecture 9 / Lab 9)
    Branches covered:
    - sign_up: empty username, short password, existing user, success
    - login: user not found, bad password, success
    - assign_role: not logged in, not admin, invalid role, self-change, target not found, success
    """

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        auth_mod.AUDIT_FILE = os.path.join(self._tmpdir.name, "audit_log.txt")
        self.repo = FakeUserRepo()
        self.auth = AuthService(self.repo)

        # Create an existing user in repo (password stored already hashed for login test)
        # We'll compute correct hash using internal method to avoid guessing hash format.
        hashed = self.auth._hash_password("password123")
        self.repo.users["existing"] = User("existing", hashed, "STAFF")

        # Admin user
        admin_hash = self.auth._hash_password("adminpass123")
        self.repo.users["admin"] = User("admin", admin_hash, "ADMIN")

    # ---- sign_up branches ----
    def test_sign_up_username_empty(self):
        with self.assertRaises(ValueError):
            self.auth.sign_up("", "password123", "STAFF")

    def test_sign_up_password_too_short(self):
        with self.assertRaises(ValueError):
            self.auth.sign_up("newuser", "short7", "STAFF")

    def test_sign_up_existing_user(self):
        with self.assertRaises(ValueError):
            self.auth.sign_up("existing", "password123", "STAFF")

    def test_sign_up_success(self):
        ok = self.auth.sign_up(" NewUser ", "password123", "manager")
        self.assertTrue(ok)
        self.assertIsNotNone(self.repo.get_user("newuser"))  # stripped+lowered
        self.assertEqual(self.repo.get_user("newuser").role, "MANAGER")  # uppered via User

    # ---- login branches ----
    def test_login_user_not_found(self):
        self.assertFalse(self.auth.login("missing", "password123"))

    def test_login_bad_password(self):
        self.assertFalse(self.auth.login("existing", "wrongpass"))

    def test_login_success(self):
        self.assertTrue(self.auth.login("existing", "password123"))
        self.assertIsNotNone(self.auth.current_user)

    # ---- assign_role branches ----
    def test_assign_role_not_logged_in(self):
        self.auth.current_user = None
        self.assertFalse(self.auth.assign_role("existing", "ADMIN"))

    def test_assign_role_not_admin(self):
        self.auth.current_user = self.repo.get_user("existing")  # STAFF
        self.assertFalse(self.auth.assign_role("existing", "ADMIN"))

    def test_assign_role_invalid_role(self):
        self.auth.current_user = self.repo.get_user("admin")
        self.assertFalse(self.auth.assign_role("existing", "INVALID"))

    def test_assign_role_cannot_change_self(self):
        self.auth.current_user = self.repo.get_user("admin")
        self.assertFalse(self.auth.assign_role("admin", "STAFF"))

    def test_assign_role_target_not_found(self):
        self.auth.current_user = self.repo.get_user("admin")
        self.assertFalse(self.auth.assign_role("missing", "STAFF"))

    def test_assign_role_success(self):
        self.auth.current_user = self.repo.get_user("admin")
        self.assertTrue(self.auth.assign_role("existing", "MANAGER"))
        self.assertEqual(self.repo.get_user("existing").role, "MANAGER")


if __name__ == "__main__":
    unittest.main()
