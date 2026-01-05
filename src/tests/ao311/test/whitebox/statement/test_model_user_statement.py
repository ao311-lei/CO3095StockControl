import unittest
from model.user import User

class TestUserStatement(unittest.TestCase):
    """
    Statement testing 
    Executes all statements in user.py at least once
    """

    def test_user_statements(self):
        u = User("alice", "pw", "admin")
        self.assertTrue(u.is_admin())
        self.assertTrue(u.is_manager())

        v = User("bob", "pw", "staff")
        self.assertFalse(v.is_admin())
        self.assertFalse(v.is_manager())

if __name__ == "__main__":
    unittest.main()
