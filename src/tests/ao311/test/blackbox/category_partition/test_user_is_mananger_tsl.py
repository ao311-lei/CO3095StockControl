"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: User.is_manager
TSL spec: specs/user_is_manager.tsl
"""

import unittest
from model.user import User


class TestUserIsManagerTSL(unittest.TestCase):
    def test_admin_role_true(self):
        # Frame: RoleState=AdminRole
        u = User("u", "p", "ADMIN")
        self.assertTrue(u.is_manager())

    def test_manager_role_true(self):
        # Frame: RoleState=ManagerRole
        u = User("u", "p", "MANAGER")
        self.assertTrue(u.is_manager())

    def test_other_role_false(self):
        # Frame: RoleState=OtherRole
        u = User("u", "p", "STAFF")
        self.assertFalse(u.is_manager())


if __name__ == "__main__":
    unittest.main()
