"""
CO3095 - White-box (Symbolic Execution)

Unit: model.user.User
Technique: Symbolic Execution (derive path conditions, then pick concrete inputs)
Tool: pytest (runner) / unittest-style asserts are fine too

Symbolic Paths:
- __init__: role.upper() -> valid if role is str; raises AttributeError if role is None
- is_admin:
    Path A: role == 'ADMIN' -> True
    Path B: role != 'ADMIN' -> False
- is_manager:
    Path C: role in {'MANAGER','ADMIN'} -> True
    Path D: role not in that set -> False
"""

import pytest
from model.user import User


def test_init_role_normalises_to_upper():
    u = User("alice", "pw", "aDmIn")
    assert u.role == "ADMIN"


def test_init_role_none_raises_attribute_error():
    with pytest.raises(AttributeError):
        User("bob", "pw", None)


def test_is_admin_true_path():
    u = User("a", "pw", "ADMIN")
    assert u.is_admin() is True


def test_is_admin_false_path():
    u = User("a", "pw", "STAFF")
    assert u.is_admin() is False


def test_is_manager_true_path_admin():
    u = User("a", "pw", "ADMIN")
    assert u.is_manager() is True


def test_is_manager_true_path_manager():
    u = User("a", "pw", "MANAGER")
    assert u.is_manager() is True


def test_is_manager_false_path():
    u = User("a", "pw", "STAFF")
    assert u.is_manager() is False
