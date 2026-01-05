from model.category import Category


class CategoryRepo:
    def __init__(self, filename):
        self.filename = filename

        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

        self.categories = []

    def add_category(self, category: Category):
        with open(self.filename, "a") as file:
            file.write(category.category_id + ":" + category.name + ":" + str(category.active) + "\n")

    def category_exists(self, name, category_name=None):
        with open(self.filename, "r") as file:
            for line in file:
                if line.strip() == name:
                    if category_name.lower() == name.lower():
                        return True
        return False


    def get_all_categories(self):
        categories = []
        with open(self.filename, "r") as file:
            for line in file:
                if line.strip():
                    category_id, name, active = line.strip().split(":")
                    categories.append(Category(category_id, name, active="True"))
        return categories

    def save(self, categories):
        with open(self.filename, "w", encoding="utf-8") as file:
            for c in categories:
                file.write(f"{c.category_id}:{c.name}:{str(bool(c.active))}\n")

    def get_by_name(self, name: str):
        name_key = name.strip().lower()
        for c in self.get_categories():
            if c.name.strip().lower() == name_key:
                return c
        return None