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

    def category_exists(self, name):
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