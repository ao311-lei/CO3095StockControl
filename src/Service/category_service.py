from model.category import Category

class CategoryService:

    def __init__(self, category_repo):
        self.category_repo = category_repo

    def create_category(self, category_id, name):
        if name.strip = "":
            raise ValueError("Category name cannot be empty")

        if self.category_repo.get_by_name(name):
            raise ValueError("Category name already exists")

        categories = self.category_repo.get_categories()

        categories.append(Category(category_id, name, True))

        self.category_repo.save(categories)

    def rename_category(self, category_id, new_name):
        if new_name.strip == "":
            raise ValueError("Category name cannot be empty")

        if self.category_repo.get_by_name(new_name):
            raise ValueError("Category name already exists")

        categories = self.category_repo.get_categories()

        for category in categories:
            if category.category_id == category_id:
                category.name = new_name
                self.category_repo.save(categories)
                return category.name

        raise ValueError("Category not found")
    def deactivate_category(self, category_id):
        categories = self.category_repo.get_categories()

        for category in categories:
            if category.category_id == category_id:
                category.deactivate()
                self.category_repo.save(categories)
                return category.name

        raise ValueError("Category not found")

    def list_categories(self):
        return self.category_repo.get_categories()