"""
CO3095 Black-box: Category Partition (TSLGenerator derived)
Target: UserRepo.update_role
TSL spec: specs/userrepo_update_role.tsl
Uses a temporary file to avoid touching real project data files.
"""

import unittest
import tempfile
import os
from Repo.user_repo import UserRepo
from model.user import User


class TestUserRepoUpdateRoleTSL(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.repo = UserRepo(self.tmp.name)

        # seed one user line: username:password:role
        with open(self.tmp.name, "w") as f:
            f.write("alice:hashed:STAFF\n")

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_invalid_role_error(self):
        # Frame: NewRole=Invalid [error]
        with self.assertRaises(ValueError):
            self.repo.update_role("alice", "CASHIER")

    def test_user_missing_returns_false(self):
        # Frame: UserExists=No, NewRole=Staff
        self.assertFalse(self.repo.update_role("missing", "STAFF"))

    def test_user_exists_updates_true(self):
        # Frame: UserExists=Yes, NewRole=Admin
        self.assertTrue(self.repo.update_role("alice", "ADMIN"))
        user = self.repo.get_user("alice")
        self.assertEqual(user.role, "ADMIN")


if __name__ == "__main__":
    unittest.main()
