"""
CO3095 - Symbolic Execution (White-box)

Unit: Service.category_service.CategoryService
Functions:
- __init__(category_repo)
- create_category()
- rename_category()
- deactivate_category()
- list_categories()

We use a fake repo to drive each branch.
"""

import pytest
from Service.category_service import CategoryService
from model.category import Category


class FakeCategoryRepo:
    def __init__(self, categories=None):
        self._categories = list(categories or [])

    def get_categories(self):
        return list(self._categories)

    def save(self, categories):
        self._categories = list(categories)

    def get_by_name(self, name):
        key = name.strip().lower()
        for c in self._categories:
            if c.name.strip().lower() == key:
                return c
        return None


def test_category_service_symbolic_all_functions():
    repo = FakeCategoryRepo([Category("C1", "Food", True)])
    svc = CategoryService(repo)

    # create_category success
    svc.create_category("C2", "Drinks")
    assert repo.get_by_name("Drinks") is not None

    # create_category empty -> raise
    with pytest.raises(ValueError):
        svc.create_category("C3", "   ")

    # create_category duplicate -> raise
    with pytest.raises(ValueError):
        svc.create_category("C4", "Food")

    # rename_category success
    assert svc.rename_category("C2", "Cold Drinks") == "Cold Drinks"

    # rename_category empty -> raise
    with pytest.raises(ValueError):
        svc.rename_category("C2", "   ")

    # rename_category duplicate -> raise
    with pytest.raises(ValueError):
        svc.rename_category("C2", "Food")

    # rename_category not found -> raise
    with pytest.raises(ValueError):
        svc.rename_category("MISSING", "X")

    # deactivate_category success
    assert svc.deactivate_category("C2") == "Cold Drinks"
    assert repo.get_by_name("Cold Drinks").active is False

    # deactivate_category not found -> raise
    with pytest.raises(ValueError):
        svc.deactivate_category("MISSING")

    # list_categories
    cats = svc.list_categories()
    assert isinstance(cats, list)
    assert len(cats) >= 1
