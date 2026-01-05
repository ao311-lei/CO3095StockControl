"""
CO3095 - Symbolic Execution (White-box)

Unit: Repo.user_repo.UserRepo
Functions:
- __init__
- load_users
- get_user
- save_user
- save_all_users
- update_role

We use a temp file as the users DB.
"""

import os
import tempfile
import pytest

from Repo.user_repo import UserRepo
from model.user import User


def test_user_repo_symbolic_all_functions():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        repo = UserRepo(tmp.name)

        # load_users empty file
        assert repo.load_users() == []

        # save_user + get_user
        repo.save_user(User("alice", "hash", "STAFF"))
        assert repo.get_user("alice") is not None

        # save_user duplicate
        with pytest.raises(Exception):
            repo.save_user(User("alice", "hash", "STAFF"))

        # save_all_users
        repo.save_all_users([User("bob", "hash2", "ADMIN")])
        assert repo.get_user("alice") is None
        assert repo.get_user("bob") is not None

        # update_role invalid role
        with pytest.raises(ValueError):
            repo.update_role("bob", "HACKER")

        # update_role success
        assert repo.update_role("bob", "MANAGER") is True
        assert repo.get_user("bob").role == "MANAGER"

        # update_role user not found
        assert repo.update_role("missing", "STAFF") is False

    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
