import unittest
from Service.category_service import CategoryService
from model.category import Category


class FakeCategoryRepo:
    def __init__(self):
        self.categories = []

    def get_by_name(self, name):
        key = name.strip().lower()
        for c in self.categories:
            if c.name.strip().lower() == key:
                return c
        return None

    def get_categories(self):
        return list(self.categories)

    def save(self, categories):
        self.categories = list(categories)


class TestCategoryServiceBranch(unittest.TestCase):
    """
    Branch testing for CategoryService:
    - create_category: empty name, duplicate name, success
    - rename_category: empty name, duplicate name, not found, success
    - deactivate_category: not found, success
    """

    def setUp(self):
        self.repo = FakeCategoryRepo()
        self.service = CategoryService(self.repo)
        self.repo.save([Category("C1", "Food", True), Category("C2", "Drinks", True)])

    def test_create_empty_name(self):
        with self.assertRaises(ValueError):
            self.service.create_category("C3", "")

    def test_create_duplicate_name(self):
        with self.assertRaises(ValueError):
            self.service.create_category("C3", "Food")

    def test_create_success(self):
        self.service.create_category("C3", "Snacks")
        self.assertIsNotNone(self.repo.get_by_name("Snacks"))

    def test_rename_empty_name(self):
        with self.assertRaises(ValueError):
            self.service.rename_category("C1", "")

    def test_rename_duplicate_name(self):
        with self.assertRaises(ValueError):
            self.service.rename_category("C1", "Drinks")

    def test_rename_not_found(self):
        with self.assertRaises(ValueError):
            self.service.rename_category("C999", "NewName")

    def test_rename_success(self):
        new_name = self.service.rename_category("C1", "Fresh Food")
        self.assertEqual(new_name, "Fresh Food")
        self.assertIsNotNone(self.repo.get_by_name("Fresh Food"))

    def test_deactivate_not_found(self):
        with self.assertRaises(ValueError):
            self.service.deactivate_category("C999")

    def test_deactivate_success(self):
        name = self.service.deactivate_category("C2")
        self.assertEqual(name, "Drinks")
        c = self.repo.get_by_name("Drinks")
        self.assertFalse(c.active)


if __name__ == "__main__":
    unittest.main()
