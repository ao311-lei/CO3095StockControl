import os
import tempfile
import pytest

from Repo.user_repo import UserRepo
from model.user import User


def test_concolic_update_role_flip_not_found_to_found():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        repo = UserRepo(tmp.name)

        # seed: user missing -> False
        assert repo.update_role("missing", "STAFF") is False

        # mutate: add user -> update True
        repo.save_user(User("alice", "hash", "STAFF"))
        assert repo.update_role("alice", "ADMIN") is True
        assert repo.get_user("alice").role == "ADMIN"

        # mutate: invalid role -> raises
        with pytest.raises(ValueError):
            repo.update_role("alice", "HACKER")
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
