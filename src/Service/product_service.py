from Repo.product_repo import ProductRepo
from Repo.category_repo import CategoryRepo


class ProductService:
    def __init__(self, product_repo: ProductRepo, category_repo: CategoryRepo):
        self.product_repo = product_repo
        self.category_repo = category_repo

    def add_new_product(self, sku, name, description, quantity, price, category=None):
        if sku == "":
            return "SKU cannot be empty"
        if name == "":
            return "Name cannot be empty"

            # Convert quantity to int
        try:
            quantity = int(quantity)
        except:
            return "Quantity must be a whole number"

        if quantity < 0:
            return "Quantity cannot be negative"

            # Convert price to float
        try:
            price = float(price)
        except:
            return "Price must be a number"

        if price < 0:
            return "Price cannot be negative"

            # Check SKU unique
        existing = self.product_repo.find_by_sku(sku)
        if existing != None:
            return "That SKU already exists"

        # Optional: category check (ONLY if you've built categories)
        # If you have category_repo and a function to check existence, use it.
        # If not, skip this part.
        # if category != None and category != "":
        #     if self.category_repo.find_by_name(category) == None:
        #         return "Category does not exist"

        # Create product + save
        new_product = Product(sku, name, description, quantity, price, category)
        self.product_repo.add_product(new_product)

        return "Product added successfully"

    def update_product(self, sku, **updates):
        pass

    def remove_product(self, sku):
        pass

    def search_products(self, query):
        pass

    def filter_by_category(self, category_name):
        pass
