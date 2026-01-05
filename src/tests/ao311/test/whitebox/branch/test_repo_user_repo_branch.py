import os
import tempfile
import unittest
from Repo.user_repo import UserRepo
from model.user import User


class TestUserRepoBranch(unittest.TestCase):
    """
    Branch testing for UserRepo.update_role:
    - invalid role -> raises ValueError
    - username not found -> False
    - username found -> True and file updated
    """

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.repo = UserRepo(self.tmp.name)

        # Seed one user line
        self.repo.save_user(User("alice", "hash", "STAFF"))

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_update_role_invalid_role_raises(self):
        with self.assertRaises(ValueError):
            self.repo.update_role("alice", "INVALID_ROLE")

    def test_update_role_user_not_found(self):
        self.assertFalse(self.repo.update_role("missing", "ADMIN"))

    def test_update_role_success(self):
        self.assertTrue(self.repo.update_role("alice", "ADMIN"))
        updated = self.repo.get_user("alice")
        self.assertEqual(updated.role, "ADMIN")


if __name__ == "__main__":
    unittest.main()
