"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: User.__init__
TSL spec: specs/user_init_role.tsl
Tooling: TSLGenerator (frames) + unittest (execution)
"""

import unittest
from src.model.user import User


class TestUserInitRoleTSL(unittest.TestCase):
    def test_admin(self):
        # Frame: Role=Admin -> "ADMIN"
        u = User("alice", "pw", "ADMIN")
        self.assertEqual(u.role, "ADMIN")

    def test_manager(self):
        # Frame: Role=Manager -> "MANAGER"
        u = User("bob", "pw", "MANAGER")
        self.assertEqual(u.role, "MANAGER")

    def test_staff_default(self):
        # Frame: Role=Staff_Default -> default used
        u = User("c", "pw")
        self.assertEqual(u.role, "STAFF")

    def test_other_valid(self):
        # Frame: Role=OtherValid -> "CASHIER"
        u = User("d", "pw", "CASHIER")
        self.assertEqual(u.role, "CASHIER")

    def test_mixed_case_admin(self):
        # Frame: Role=MixedCaseAdmin -> "aDmIn" -> "ADMIN"
        u = User("e", "pw", "aDmIn")
        self.assertEqual(u.role, "ADMIN")

    def test_empty_string(self):
        # Frame: Role=EmptyString -> ""
        u = User("f", "pw", "")
        self.assertEqual(u.role, "")

    def test_none_role_error(self):
        # Frame: Role=NoneRole [error] -> AttributeError
        with self.assertRaises(AttributeError):
            User("g", "pw", None)


if __name__ == "__main__":
    unittest.main()
