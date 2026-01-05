"""
CO3095 - White-box (Concolic Testing)

Idea:
Start with a concrete input, observe path, then mutate input to flip the next predicate.

Unit: model.user.User
Predicates:
- is_admin: role == 'ADMIN'
- is_manager: role in {'MANAGER','ADMIN'}
"""

from model.user import User


def test_concolic_flip_is_admin():
    # Seed input -> False path
    u = User("x", "pw", "STAFF")
    assert u.is_admin() is False

    # Flip constraint role == 'ADMIN' -> True path
    u2 = User("x", "pw", "ADMIN")
    assert u2.is_admin() is True


def test_concolic_flip_is_manager():
    # Seed -> False path
    u = User("x", "pw", "STAFF")
    assert u.is_manager() is False

    # Flip to MANAGER -> True
    u2 = User("x", "pw", "MANAGER")
    assert u2.is_manager() is True

    # Flip to ADMIN -> also True (different satisfying assignment)
    u3 = User("x", "pw", "ADMIN")
    assert u3.is_manager() is True
