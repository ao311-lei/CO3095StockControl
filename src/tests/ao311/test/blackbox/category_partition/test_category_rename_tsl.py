import unittest
from Service.category_service import CategoryService
from model.category import Category


class FakeCategoryRepo:
    def __init__(self):
        self.categories = []

    def get_by_name(self, name):
        for c in self.categories:
            if c.name.lower() == name.lower():
                return c
        return None

    def get_categories(self):
        return self.categories

    def save(self, categories):
        self.categories = categories


class TestCategoryRenameTSL(unittest.TestCase):

    def setUp(self):
        self.repo = FakeCategoryRepo()
        self.repo.categories.append(Category("C1", "Food", True))
        self.service = CategoryService(self.repo)

    def test_rename_success(self):
        # Frame: CategoryID=Exists, NewName=UniqueValid
        new_name = self.service.rename_category("C1", "Groceries")
        self.assertEqual(new_name, "Groceries")

    def test_category_not_found(self):
        # Frame: CategoryID=DoesNotExist [error]
        with self.assertRaises(ValueError):
            self.service.rename_category("C99", "Other")

    def test_duplicate_name_error(self):
        # Frame: NewName=Duplicate [error]
        self.repo.categories.append(Category("C2", "Drinks", True))
        with self.assertRaises(ValueError):
            self.service.rename_category("C1", "Drinks")


if __name__ == "__main__":
    unittest.main()
