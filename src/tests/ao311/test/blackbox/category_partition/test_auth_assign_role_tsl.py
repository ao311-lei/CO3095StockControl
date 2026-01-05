"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: AuthService.assign_role
TSL spec: specs/auth_assign_role.tsl
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

    def update_role(self, username, new_role):
        u = self.users.get(username)
        if u is None:
            return False
        u.role = new_role.strip().upper()
        return True


class TestAuthAssignRoleTSL(unittest.TestCase):
    def setUp(self):
        self.repo = FakeUserRepo()
        self.auth = AuthService(self.repo)
        self.auth.write_audit = lambda msg: None  # avoid file writes

        self.repo.save_user(User("admin", "x", "ADMIN"))
        self.repo.save_user(User("bob", "x", "STAFF"))

    def test_not_logged_in_false(self):
        # Frame: LoggedIn=No
        self.auth.current_user = None
        self.assertFalse(self.auth.assign_role("bob", "MANAGER"))

    def test_logged_in_not_admin_false(self):
        # Frame: LoggedIn=YesNotAdmin
        self.auth.current_user = User("staff", "x", "STAFF")
        self.assertFalse(self.auth.assign_role("bob", "MANAGER"))

    def test_invalid_new_role_false(self):
        # Frame: LoggedIn=YesAdmin, NewRole=Invalid
        self.auth.current_user = self.repo.get_user("admin")
        self.assertFalse(self.auth.assign_role("bob", "CASHIER"))

    def test_self_target_false(self):
        # Frame: TargetUser=Self
        self.auth.current_user = self.repo.get_user("admin")
        self.assertFalse(self.auth.assign_role("admin", "STAFF"))

    def test_target_missing_false(self):
        # Frame: TargetUser=OtherMissing
        self.auth.current_user = self.repo.get_user("admin")
        self.assertFalse(self.auth.assign_role("missing", "MANAGER"))

    def test_valid_change_true(self):
        # Frame: LoggedIn=YesAdmin, NewRole=Manager, TargetUser=OtherExists
        self.auth.current_user = self.repo.get_user("admin")
        self.assertTrue(self.auth.assign_role("bob", "MANAGER"))
        self.assertEqual(self.repo.get_user("bob").role, "MANAGER")


if __name__ == "__main__":
    unittest.main()
