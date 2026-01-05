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


class TestCategoryServiceStatement(unittest.TestCase):
    """Statement testing for Service.category_service"""

    def setUp(self):
        self.repo = FakeCategoryRepo()
        self.repo.save([Category("C1", "Food", True)])
        self.svc = CategoryService(self.repo)

    def test_category_service_statements(self):
        self.svc.create_category("C2", "Drinks")
        self.assertIsNotNone(self.repo.get_by_name("Drinks"))

        new_name = self.svc.rename_category("C2", "Cold Drinks")
        self.assertEqual(new_name, "Cold Drinks")

        deactivated = self.svc.deactivate_category("C2")
        self.assertEqual(deactivated, "Cold Drinks")
        self.assertFalse(self.repo.get_by_name("Cold Drinks").active)

        cats = self.svc.list_categories()
        self.assertTrue(len(cats) >= 1)


if __name__ == "__main__":
    unittest.main()
