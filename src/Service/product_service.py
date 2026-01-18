from Repo.product_repo import ProductRepo
from Repo.category_repo import CategoryRepo
from model.product import Product
from datetime import datetime
import csv

AUDIT_FILE = "src/data/audit_log.txt"


class ProductService:
    def __init__(self, product_repo: ProductRepo, category_repo: CategoryRepo):
        self.product_repo = product_repo
        self.category_repo = category_repo

    def add_new_product(self, sku, name, description, quantity, price, category=None, user=None):
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
        self.write_audit(f"USER={user} ACTION=PRODUCT_ADD sku={sku} qty={quantity} price={price}")

        return "Product added successfully"

    def update_product(self, sku, name, description, quantity, price, category,user=None):
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
            self.write_audit(f"USER={user} ACTION=PRODUCT_UPDATE sku={sku}")
            return "Product updated successfully"
        else:
            return "Product not found"

    def remove_product(self, sku, user=None):
        if sku == "":
            return "SKU cannot be empty"

        existing = self.product_repo.find_by_sku(sku)
        if existing == None:
            return "Product not found"

        removed = self.product_repo.remove_by_sku(sku)
        if removed:
            self.write_audit(f"USER={user} ACTION=PRODUCT_REMOVE sku={sku}")
            return "Product removed successfully"
        else:
            return "Product not found"

    def deactivate_product(self, sku, user=None):
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
        self.write_audit(f"USER={user} ACTION=PRODUCT_DEACTIVATE sku={sku}")
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

    def update_product_description(self, sku, description):
        if sku is None or sku.strip() == "":
            raise ValueError("SKU cannot be empty")

        product = self.product_repo.get_product(sku)
        if product is None:
            raise ValueError("Product not found")

        if description is None or description.strip() == "":
            raise ValueError("Description cannot be empty")

        description = description.strip()

        if len(description) > 300:
            raise ValueError("Description too long (max 300 characters)")

        if product.description == description:
            raise ValueError("Description is unchanged")

        product.description = description
        self.product_repo.update_product(sku, description=description)

        return product.description


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

    def write_audit(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(AUDIT_FILE, "a") as f:
            f.write(f"{timestamp} - {message}\n")



    def bulk_import_products(self, csv_path, mode="skip", user=None):
        """
        Bulk import products from a CSV file.

        The expected header is:
        sku,name,description,quantity,price,category,active

        modes:
          - skip: if SKU exists, skip it
          - upsert: if SKU exists, overwrite it. Or else add it
        """

        summary = {
            "rows_read": 0,
            "added": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }


        mode = (mode or "skip").strip().lower()
        if mode not in ["skip", "upsert"]:
            summary["errors"].append("Invalid mode. Use 'skip' or 'upsert'.")
            return summary

        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                required = ["sku", "name", "description", "quantity", "price"]
                for r in required:
                    if r not in reader.fieldnames:
                        summary["errors"].append(f"Missing required column: {r}")
                        return summary

                for idx, row in enumerate(reader, start=2):
                    summary["rows_read"] += 1

                    try:
                        sku = (row.get("sku") or "").strip()
                        name = (row.get("name") or "").strip()
                        description = (row.get("description") or "").strip()
                        quantity_raw = (row.get("quantity") or "").strip()
                        price_raw = (row.get("price") or "").strip()
                        category = (row.get("category") or "").strip()
                        active_raw = (row.get("active") or "").strip().upper()

                        if category == "":
                            category = None

                        if sku == "" or name == "":
                            raise ValueError("SKU and name are required.")

                        try:
                            quantity = int(quantity_raw)
                        except:
                            raise ValueError("Quantity must be a whole number.")

                        if quantity < 0:
                            raise ValueError("Quantity cannot be negative.")

                        try:
                            price = float(price_raw)
                        except:
                            raise ValueError("Price must be a number.")

                        if price < 0:
                            raise ValueError("Price cannot be negative.")

                        existing = self.product_repo.find_by_sku(sku)

                        # Determine active state (optional column)
                        active = True
                        if active_raw == "INACTIVE":
                            active = False
                        elif active_raw in ["", "ACTIVE"]:
                            active = True
                        else:
                            if row.get("active") is not None and row.get("active") != "":
                                raise ValueError("Active must be ACTIVE or INACTIVE.")

                        if existing is None:
                            # Add
                            new_product = Product(sku, name, description, quantity, price, category, active=active)
                            self.product_repo.add_product(new_product)
                            summary["added"] += 1
                        else:
                            # Exists
                            if mode == "skip":
                                summary["skipped"] += 1
                            else:
                                # upsert -> overwrite ting
                                existing.name = name
                                existing.description = description
                                existing.quantity = quantity
                                existing.price = price
                                existing.category = category
                                existing.active = active
                                self.product_repo.save_product(existing)
                                summary["updated"] += 1

                    except Exception as e:
                        summary["errors"].apend(f"Row {idx}: {str(e)}")

            self.write_audit(
                f"USER={user} ACTION=PRODUCT_BULK_IMPORT path={csv_path} mode={mode} "
                f"added={summary['added']} updated={summary['updated']} skipped={summary['skipped']} "
                f"errors={len(summary['errors'])}"
            )

            return summary

        except FileNotFoundError:
            summary["errors"].apend("CSV file not found.")
            return summary
        except Exception as e:
            summary["errors"].append(f"Failed to read CSV: {str(e)}")
            return summary
