import unittest
from model.user import User


class TestUserBranch(unittest.TestCase):
    """
    CO3095 White-box Branch Testing (Lecture 9 / Lab 9)

    Goal: execute both True/False outcomes of role checks.
    """

    def test_is_admin_true(self):
        u = User("a", "pw", "ADMIN")
        self.assertTrue(u.is_admin())

    def test_is_admin_false(self):
        u = User("a", "pw", "STAFF")
        self.assertFalse(u.is_admin())

    def test_is_manager_true_manager(self):
        u = User("a", "pw", "MANAGER")
        self.assertTrue(u.is_manager())

    def test_is_manager_true_admin(self):
        u = User("a", "pw", "ADMIN")
        self.assertTrue(u.is_manager())

    def test_is_manager_false(self):
        u = User("a", "pw", "STAFF")
        self.assertFalse(u.is_manager())


if __name__ == "__main__":
    unittest.main()
