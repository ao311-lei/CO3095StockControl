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


def test_concolic_create_category_flip_conditions():
    repo = FakeCategoryRepo([Category("C1", "Food", True)])
    svc = CategoryService(repo)

    # seed: empty name -> error
    with pytest.raises(ValueError):
        svc.create_category("C2", "   ")

    # mutate: valid name but duplicate -> error
    with pytest.raises(ValueError):
        svc.create_category("C2", "Food")

    # mutate: valid + new -> success
    svc.create_category("C2", "Drinks")
    assert repo.get_by_name("Drinks") is not None


def test_concolic_rename_flip_not_found_to_found():
    repo = FakeCategoryRepo([Category("C1", "Food", True)])
    svc = CategoryService(repo)

    # seed: not found -> error
    with pytest.raises(ValueError):
        svc.rename_category("MISSING", "X")

    # mutate: now use existing id -> success
    assert svc.rename_category("C1", "Fresh Food") == "Fresh Food"
