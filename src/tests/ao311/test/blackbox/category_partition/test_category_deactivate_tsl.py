import unittest
from Service.category_service import CategoryService
from model.category import Category


class FakeCategoryRepo:
    def __init__(self):
        self.categories = []

    def get_categories(self):
        return self.categories

    def save(self, categories):
        self.categories = categories


class TestCategoryDeactivateTSL(unittest.TestCase):

    def setUp(self):
        self.repo = FakeCategoryRepo()
        self.repo.categories.append(Category("C1", "Food", True))
        self.service = CategoryService(self.repo)

    def test_deactivate_success(self):
        # Frame: CategoryID=Exists
        name = self.service.deactivate_category("C1")
        self.assertEqual(name, "Food")
        self.assertFalse(self.repo.categories[0].active)

    def test_category_not_found(self):
        # Frame: CategoryID=DoesNotExist [error]
        with self.assertRaises(ValueError):
            self.service.deactivate_category("C99")


if __name__ == "__main__":
    unittest.main()
