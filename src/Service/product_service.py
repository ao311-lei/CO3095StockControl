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

        new_product = Product(sku, name, description, quantity, price, category, active=True)
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

    def deactivate_product(self, sku):
        sku = (sku or "").strip()
        if sku == "":
            return "SKU cannot be empty"

        p = self.product_repo.find_by_sku(sku)
        if p is None:
            return "Product not found"

        if p.active is False:
            return "Product is already INACTIVE"

        p.active = False
        self.product_repo.save_product(p)
        return "Product deactivated successfully"

    def reactivate_product(self, sku):
        sku = (sku or "").strip()
        if sku == "":
            return "SKU cannot be empty"

        p = self.product_repo.find_by_sku(sku)
        if p is None:
            return "Product not found"

        if p.active is True:
            return "Product is already ACTIVE"

        p.active = True
        self.product_repo.save_product(p)
        return "Product reactivated successfully"

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
            # HIGHEST PRIORITY: inactive
            if p.active is False:
                results.append((p, "INACTIVE"))
                continue

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

        for p in self.product_repo.get_all_products():
            # NEW: ignore inactive for alerts
            if getattr(p, "active", True) is False:
                continue

                # convert quantity safely (txt files often load as strings)
            try:
                qty = int(p.quantity)
            except:
                continue  # skip broken data

                # match the same rule as status labels (LOW STOCK when qty <= threshold)
            if qty <= threshold:
                low_stock.append(p)

        return low_stock

    def get_dashboard_summary(self, threshold=5):
        products = self.product_repo.get_all_products()

        total_products = len(products)
        total_units = 0
        low_stock_count = 0
        out_of_stock_count = 0

        for p in products:
            qty = int(p.quantity)
            total_units += qty

            if qty == 0:
                out_of_stock_count += 1
            elif qty < threshold:
                low_stock_count += 1

        if out_of_stock_count > 0:
            system_status = "CRITICAL"
        elif low_stock_count >= 3:
            system_status = "WARNING"
        else:
            system_status = "HEALTHY"

        if total_products > 0:
            low_stock_percent = round((low_stock_count / total_products) * 100, 1)
            out_of_stock_percent = round((out_of_stock_count / total_products) * 100, 1)
        else:
            low_stock_percent = 0
            out_of_stock_percent = 0

        return {
            "total_products": total_products,
            "total_units": total_units,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "threshold": threshold,
            "system_status": system_status,
            "low_stock_percent": low_stock_percent,
            "out_of_stock_percent": out_of_stock_percent,


        }

    def estimate_restock_cost_for_sku(self, sku, target_stock_level):
        sku = (sku or "").strip()
        if sku == "":
            return None, "SKU cannot be empty."

        try:
            target_stock_level = int(target_stock_level)
        except:
            return None, "Target stock level must be a whole number."

        if target_stock_level < 0:
            return None, "Target stock level cannot be negative."

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            return None, "Product not found."

        # ignore inactive products
        if getattr(product, "active", True) is False:
            return None, "This product is INACTIVE. Reactivate it before planning restock."

        try:
            current_qty = int(product.quantity)
            unit_price = float(product.price)
        except:
            return None, "Product data is invalid (quantity/price)."

        if current_qty >= target_stock_level:
            return None, "This product is already at or above the target stock level."

        units_to_buy = target_stock_level - current_qty
        estimated_cost = units_to_buy * unit_price

        estimate = {
            "sku": product.sku,
            "name": product.name,
            "current_qty": current_qty,
            "target_qty": target_stock_level,
            "units_to_buy": units_to_buy,
            "unit_price": unit_price,
            "estimated_cost": estimated_cost
        }

        return estimate, None

    def estimate_restock_cost_for_multiple_skus(self, sku_targets):
        breakdown = []
        total_cost = 0.0
        errors = []

        for sku, target in sku_targets:
            estimate, error = self.estimate_restock_cost_for_sku(sku, target)

            if error is not None:
                errors.append(f"{sku}: {error}")
                continue

            breakdown.append(estimate)
            total_cost += float(estimate["estimated_cost"])

        return breakdown, total_cost, errors



