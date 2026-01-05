import os
import tempfile
import pytest

import Service.auth_service as auth_mod
from Service.auth_service import AuthService
from model.user import User


class FakeUserRepo:
    def __init__(self):
        self.users = {}

    def get_user(self, username):
        return self.users.get(username)

    def save_user(self, user):
        self.users[user.username] = user

    def update_role(self, username, new_role):
        u = self.users.get(username)
        if u is None:
            return False
        u.role = new_role
        return True


def test_concolic_signup_flip_paths():
    tmpdir = tempfile.TemporaryDirectory()
    try:
        auth_mod.AUDIT_FILE = os.path.join(tmpdir.name, "audit.txt")
        repo = FakeUserRepo()
        auth = AuthService(repo)

        # seed: empty username -> error
        with pytest.raises(ValueError):
            auth.sign_up("   ", "password123", "STAFF")

        # mutate: short password -> error
        with pytest.raises(ValueError):
            auth.sign_up("newuser", "short7", "STAFF")

        # mutate: success
        assert auth.sign_up("newuser", "password123", "STAFF") is True
    finally:
        tmpdir.cleanup()


def test_concolic_login_flip_paths():
    tmpdir = tempfile.TemporaryDirectory()
    try:
        auth_mod.AUDIT_FILE = os.path.join(tmpdir.name, "audit.txt")
        repo = FakeUserRepo()
        auth = AuthService(repo)

        repo.users["existing"] = User("existing", auth._hash_password("password123"), "STAFF")

        # seed: missing -> False
        assert auth.login("missing", "password123") is False

        # mutate: existing + wrong pw -> False
        assert auth.login("existing", "wrongpass") is False

        # mutate: existing + correct -> True
        assert auth.login("existing", "password123") is True
    finally:
        tmpdir.cleanup()
