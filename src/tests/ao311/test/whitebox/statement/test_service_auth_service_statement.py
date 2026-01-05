import unittest
import tempfile
import os
from Service.auth_service import AuthService
from Service import auth_service as auth_mod
from model.user import User

class FakeUserRepo:
    def __init__(self):
        self.users = {}

    def get_user(self, u):
        return self.users.get(u)

    def save_user(self, u):
        self.users[u.username] = u

    def update_role(self, u, r):
        if u in self.users:
            self.users[u].role = r
            return True
        return False

class TestAuthServiceStatement(unittest.TestCase):
    """
    Statement testing for AuthService
    """

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        auth_mod.AUDIT_FILE = os.path.join(self.tmpdir.name, "audit.txt")

        self.repo = FakeUserRepo()
        self.svc = AuthService(self.repo)

        h = self.svc._hash_password("password123")
        self.repo.users["alice"] = User("alice", h, "STAFF")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_auth_service_statements(self):
        self.svc.login("alice", "password123")
        self.svc.sign_up("bob", "password123", "MANAGER")

if __name__ == "__main__":
    unittest.main()
