"""
CO3095 - Symbolic Execution (White-box)

Unit: Service.auth_service.AuthService
Functions:
- __init__
- _hash_password
- sign_up
- login
- assign_role
- logout
- write_audit

We patch AUDIT_FILE to temp to avoid FileNotFoundError.
"""

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


def test_auth_service_symbolic_all_functions(capsys):
    tmpdir = tempfile.TemporaryDirectory()
    try:
        auth_mod.AUDIT_FILE = os.path.join(tmpdir.name, "audit_log.txt")

        repo = FakeUserRepo()
        auth = AuthService(repo)

        # __init__ + _hash_password
        hashed = auth._hash_password("password123")
        assert isinstance(hashed, str)

        # seed existing + admin
        repo.users["existing"] = User("existing", hashed, "STAFF")
        repo.users["admin"] = User("admin", auth._hash_password("adminpass123"), "ADMIN")

        # sign_up branches
        with pytest.raises(ValueError):
            auth.sign_up("   ", "password123", "STAFF")
        with pytest.raises(ValueError):
            auth.sign_up("new", "short7", "STAFF")
        with pytest.raises(ValueError):
            auth.sign_up("existing", "password123", "STAFF")

        assert auth.sign_up("NewUser", "password123", "MANAGER") is True
        assert repo.get_user("newuser") is not None

        # login branches
        assert auth.login("mxisting", "wrongpass") is False
        assert auth.login("eissing", "password123") is False
        assert auth.login("existing", "password123") is True

        # assign_role branches
        auth.current_user = None
        assert auth.assign_role("existing", "MANAGER") is False
        assert "You must be logged in" in capsys.readouterr().out

        auth.current_user = repo.get_user("existing")
        assert auth.assign_role("admin", "MANAGER") is False
        assert "Access denied" in capsys.readouterr().out

        auth.current_user = repo.get_user("admin")
        assert auth.assign_role("existing", "HACKER") is False
        assert "Invalid role" in capsys.readouterr().out

        assert auth.assign_role("admin", "MANAGER") is False
        assert "can't change your own role" in capsys.readouterr().out.lower()

        assert auth.assign_role("unknown", "MANAGER") is False
        assert "User not found" in capsys.readouterr().out

        assert auth.assign_role("existing", "MANAGER") is True
        assert "successfully changed role" in capsys.readouterr().out.lower()

        # logout
        assert auth.logout() is True
        assert auth.current_user is None

        # write_audit direct
        auth.write_audit("hello")
        assert os.path.exists(auth_mod.AUDIT_FILE)

    finally:
        tmpdir.cleanup()
