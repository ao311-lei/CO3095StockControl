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


class TestCategoryCreateTSL(unittest.TestCase):

    def setUp(self):
        self.repo = FakeCategoryRepo()
        self.service = CategoryService(self.repo)

    def test_empty_name_error(self):
        # Frame: Name=Empty [error]
        with self.assertRaises(ValueError):
            self.service.create_category("C1", "")

    def test_valid_new_category(self):
        # Frame: Name=NewValid
        self.service.create_category("C1", "Food")
        self.assertEqual(len(self.repo.categories), 1)

    def test_duplicate_name_error(self):
        # Frame: Name=Duplicate [error]
        self.repo.categories.append(Category("C1", "Food", True))
        with self.assertRaises(ValueError):
            self.service.create_category("C2", "Food")


if __name__ == "__main__":
    unittest.main()
