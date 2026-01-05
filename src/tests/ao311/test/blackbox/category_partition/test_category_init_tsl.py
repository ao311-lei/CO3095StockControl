import unittest
from model.category import Category


class TestCategoryInitTSL(unittest.TestCase):

    def test_valid_active_true(self):
        c = Category("C1", "Food", True)
        self.assertTrue(c.active)

    def test_valid_active_false(self):
        c = Category("C2", "Drinks", False)
        self.assertFalse(c.active)

    def test_empty_name_allowed(self):
        # Category has no validation responsibility
        c = Category("C3", "", True)
        self.assertEqual(c.name, "")


if __name__ == "__main__":
    unittest.main()
