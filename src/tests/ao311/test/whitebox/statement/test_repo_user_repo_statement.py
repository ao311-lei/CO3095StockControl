import unittest
import tempfile
import os
from Repo.user_repo import UserRepo
from model.user import User

class TestUserRepoStatement(unittest.TestCase):
    """
    Statement testing for UserRepo
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.repo = UserRepo(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_user_repo_statements(self):
        u = User("alice", "pw", "STAFF")
        self.repo.save_user(u)
        found = self.repo.get_user("alice")
        self.assertIsNotNone(found)

if __name__ == "__main__":
    unittest.main()
