from Repo.product_repo import ProductRepo
from Repo.category_repo import CategoryRepo
from model.product import Product


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

        new_product = Product(sku, name, description, quantity, price, category)
        self.product_repo.add_product(new_product)

        return "Product added successfully"

    def update_product(self, sku, name, description, quantity, price, category):
        if sku == "":
            return "SKU cannot be empty"

        existing = self.product_repo.find_by_sku(sku)
        if existing == None:
            return "Product not found"

        if name == "":
            return "Name cannot be empty"

        # quantity
        try:
            quantity = int(quantity)
        except:
            return "Quantity must be a whole number"
        if quantity < 0:
            return "Quantity cannot be negative"

        # price
        try:
            price = float(price)
        except:
            return "Price must be a number"
        if price < 0:
            return "Price cannot be negative"

        updated = self.product_repo.update_product(
            sku, name, description, quantity, price, category
        )

        if updated:
            return "Product updated successfully"
        else:
            return "Product not found"

    def remove_product(self, sku):
        if sku == "":
            return "SKU cannot be empty"

        existing = self.product_repo.find_by_sku(sku)
        if existing == None:
            return "Product not found"

        removed = self.product_repo.remove_by_sku(sku)
        if removed:
            return "Product removed successfully"
        else:
            return "Product not found"

    def search_products(self, query):

        q = (query or "").strip().lower()
        results = []

        if q == "":
            return results

        for p in self.product_repo.get_all_products():
            sku = str(p.sku).strip().lower()
            name = str(p.name).strip().lower()
            desc = str(p.description).strip().lower()

            if q in sku or q in name or q in desc:
                results.append(p)

        return results

    def filter_products(self, category=None, max_qty=None, sort_by=None):
        products = self.product_repo.get_all_products()
        results = []

        # Filter by category
        if category and category.strip() != "":
            cat = category.strip().lower()
            for p in products:
                if p.category is not None and p.category.strip().lower() == cat:
                    results.append(p)
        else:
            results = list(products)

        # Filter by max quantity
        if max_qty is not None and str(max_qty).strip() != "":
            try:
                max_qty = int(max_qty)
                results = [p for p in results if int(p.quantity) <= max_qty]
            except:
                pass

        # Sort
        if sort_by == "name":
            results.sort(key=lambda p: str(p.name).lower())
        elif sort_by == "quantity":
            results.sort(key=lambda p: int(p.quantity))
        elif sort_by == "price":
            results.sort(key=lambda p: float(p.price))

        return results

    def view_all_products_with_status(self, low_stock=5):
        products = self.product_repo.get_all_products()
        results = []

        for p in products:
            qty = int(p.quantity)

            if qty == 0:
                status = "OUT OF STOCK"
            elif qty <= low_stock:
                status = "LOW STOCK"
            else:
                status = "IN STOCK"

            results.append((p, status))

        return results

    def get_low_stock_products(self, threshold):
        low_stock = []

        # basic validation
        try:
            threshold = int(threshold)
        except:
            return None  # invalid threshold

        if threshold < 0:
            return None

        products = self.product_repo.get_all_products()

        for p in products:
            if int(p.quantity) < threshold:
                low_stock.append(p)

        return low_stock