"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: User.is_admin
TSL spec: specs/user_is_admin.tsl
"""

import unittest
from src.model.user import User


class TestUserIsAdminTSL(unittest.TestCase):
    def test_admin_role_true(self):
        # Frame: RoleState=AdminRole
        u = User("u", "p", "ADMIN")
        self.assertTrue(u.is_admin())

    def test_non_admin_role_false(self):
        # Frame: RoleState=NonAdminRole
        u = User("u", "p", "STAFF")
        self.assertFalse(u.is_admin())


if __name__ == "__main__":
    unittest.main()
