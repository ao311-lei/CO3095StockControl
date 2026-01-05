"""
CO3095 - Symbolic Execution (White-box)

Unit: model.category.Category
Functions:
- __init__(category_id, name, active=True)
- deactivate()

Symbolic paths:
- deactivate: sets active=False (single path)
"""

from model.category import Category


def test_category_init_and_deactivate_symbolic():
    c = Category("C1", "Food", True)
    assert c.category_id == "C1"
    assert c.name == "Food"
    assert c.active is True

    c.deactivate()
    assert c.active is False
