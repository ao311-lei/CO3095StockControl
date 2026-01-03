"""
CO3095 - Black-box Testing (Category Partition using TSLGenerator)

Technique: Category Partition (role categories)
Tooling:
- TSLGenerator used to generate test frames (see specs/user_role)
- unittest used to implement derived concrete test cases

Expected vs Actual:
- Each test states the expected behaviour and asserts the actual behaviour.

Reference lab: Category Partition + TSLGenerator workflow. :contentReference[oaicite:3]{index=3}
"""

import unittest
from src.model.user import User


class TestUserInitCategoryPartition(unittest.TestCase):
    # Frame: Admin -> "ADMIN"
    def test_init_role_admin(self):
        # Expected: role stored as "ADMIN"
        u = User("alice", "pw", "ADMIN")
        self.assertEqual(u.role, "ADMIN")  # Actual

    # Frame: Manager -> "MANAGER"
    def test_init_role_manager(self):
        # Expected: role stored as "MANAGER"
        u = User("bob", "pw", "MANAGER")
        self.assertEqual(u.role, "MANAGER")

    # Frame: OtherValid -> "CASHIER"
    def test_init_role_other_valid(self):
        # Expected: role stored as "CASHIER"
        u = User("c", "pw", "CASHIER")
        self.assertEqual(u.role, "CASHIER")

    # Frame: MixedCaseAdmin -> "aDmIn"
    def test_init_role_mixed_case_admin(self):
        # Expected: role normalised to "ADMIN"
        u = User("d", "pw", "aDmIn")
        self.assertEqual(u.role, "ADMIN")

    # Frame: EmptyString -> ""
    def test_init_role_empty_string(self):
        # Expected: role stored as "" (empty)
        u = User("e", "pw", "")
        self.assertEqual(u.role, "")

    # Frame: NoneRole -> None [error]
    def test_init_role_none_raises(self):
        # Expected: AttributeError (None has no upper())
        with self.assertRaises(AttributeError):
            User("f", "pw", None)


if __name__ == "__main__":
    unittest.main()
