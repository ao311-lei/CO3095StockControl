from model.category import Category

class CategoryService:

    def __init__(self, category_repo):
        self.category_repo = category_repo

    def create_category(self, category_id, name):
        pass

    def rename_category(self, category_id, new_name):
        pass

    def deactivate_category(self, category_id):
        pass

    def list_categories(self):
        pass