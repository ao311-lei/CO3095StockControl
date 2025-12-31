from model.menus import Menus
from Repo.product_repo import ProductRepo
from Service.product_service import ProductService
from Repo.user_repo import UserRepo
from Repo.stock_repo import StockRepo
from Service.auth_service import AuthService
from Service.stock_service import StockService
from Service.purchase_order_service import PurchaseOrderService
from Repo.favourite_repo import FavouriteRepo
from Service.favourite_service import FavouriteService
from Repo.return_repo import ReturnRepo
from Service.return_service import ReturnService
from Repo.budget_repo import BudgetRepo
from Service.budget_service import BudgetService



def press_enter_to_go_back():
    input("\nPress Enter to go back...")

def show_products_and_favourite(products, favourite_service):
    if not products:
        print("No products found.")
        return

    print("\n--- Products ---")
    for p in products:
        print(f"{p.sku} | {p.name} | {p.description} | Qty: {p.quantity} | £{p.price} | {p.category}")

    while True:
        sku = input("Enter SKU to favourite (or press Enter to go back): ").strip()
        if sku == "":
            break
        print(favourite_service.favourite_product(sku))


def stock_menu(menus, auth_service, stock_service):
    while True:
        choice = menus.view_stock_menu()

        if choice == "1":
            sku = input("Enter SKU to increase stock: ").strip()

            product = stock_service.product_repo.find_by_sku(sku)
            if product is None:
                print("Invalid SKU")
                continue

            print(f"Current quantity for {sku}: {product.quantity}")

            amount_str = input("Enter amount to increase by: ").strip()

            try:
                amount = int(amount_str)
                new_qty = stock_service.record_stock_increase(sku, amount)
                print(f"Stock updated. New quantity for {sku}: {new_qty}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            sku = input("Enter SKU to decrease stock: ").strip()

            product = stock_service.product_repo.find_by_sku(sku)
            if product is None:
                print("Invalid SKU")
                continue

            print(f"Current quantity for {sku}: {product.quantity}")

            amount_str = input("Enter amount to decrease by: ").strip()

            try:
                amount = int(amount_str)
                new_qty = stock_service.record_stock_decrease(sku, amount)
                print(f"Stock updated. New quantity for {sku}: {new_qty}")
            except ValueError as e:
                print(f"Error: {e}")


        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

def add_product_menu(product_service):
    while True:
        sku = input("Enter SKU (or press Enter to go back): ").strip()
        if sku == "":
            break

        name = input("Enter name: ").strip()
        description = input("Enter description: ").strip()
        quantity = input("Enter quantity: ").strip()
        price = input("Enter price: ").strip()
        category = input("Enter category (optional): ").strip()

        if category == "":
            category = None

        result = product_service.add_new_product(sku, name, description, quantity, price, category)
        print(result)


def remove_product_menu(product_service):
    while True:
        sku = input("Enter SKU to remove a product (or press Enter to go back): ").strip()
        # Press Enter = return to Products menu
        if sku == "":
            break
        result = product_service.remove_product(sku)
        print(result)

def update_product_menu(product_service):
    while True:
        sku = input("Enter SKU to update (or press Enter to go back): ").strip()
        if sku == "":
            break
        # Find existing product so we can show current values
        product = product_service.product_repo.find_by_sku(sku)
        if product == None:
            print("Product not found")
            return

        print("Press Enter to keep the current value.")

        name = input("Name (" + product.name + "): ").strip()
        if name == "":
            name = product.name

        description = input("Description (" + product.description + "): ").strip()
        if description == "":
            description = product.description

        quantity = input("Quantity (" + str(product.quantity) + "): ").strip()
        if quantity == "":
            quantity = str(product.quantity)

        price = input("Price (" + str(product.price) + "): ").strip()
        if price == "":
            price = str(product.price)

        current_category = ""
        if product.category != None:
            current_category = product.category

        category = input("Category (" + current_category + "): ").strip()
        if category == "":
            category = product.category  # keep as is (could be None)

        result = product_service.update_product(sku, name, description, quantity, price, category)
        print(result)

def favourite_prompt(favourite_service):

    while True:
        sku = input("Enter SKU to favourite (or press Enter to go back): ").strip()
        if sku == "":
            break
        print(favourite_service.favourite_product(sku))


def low_stock_alerts_menu(product_service, low_stock_threshold):
    low_stock = product_service.get_low_stock_products(low_stock_threshold)

    if low_stock is None:
        print("Threshold must be a whole number (0 or more).")
        return

    if len(low_stock) == 0:
        print("No low stock alerts. All products are above the threshold.")
    else:
        print("\n!! LOW STOCK ALERTS !!")
        print(f"(Threshold: {low_stock_threshold})")
        for p in low_stock:
            print(p.sku + " - " + p.name + " (Qty: " + str(p.quantity) + ")")
    press_enter_to_go_back()

def set_low_stock_threshold(current_threshold):
    print(f"Current low stock threshold is: {current_threshold}")
    new_value = input("Enter new low stock threshold (whole number, e.g. 5): ").strip()

    if new_value == "":
        print("No change made.")
        return current_threshold

    try:
        value = int(new_value)
        if value < 0:
            print("Threshold cannot be negative. Keeping current.")
            return current_threshold
        print(f"Threshold updated to: {value}")
        return value
    except ValueError:
        print("Invalid number. Keeping current.")
        return current_threshold


def products_menu(menus, product_service,favourite_service, auth_service, low_stock_threshold):

    while True:
        choice = menus.view_products_menu()

        if choice == "1":

            items = product_service.view_all_products_with_status(low_stock=low_stock_threshold)

            if not items:
                print("No products found.")
            else:
                print("\n--- All Products (Inventory Status) ---")
                print(f"(Threshold: {low_stock_threshold})")
                for p, status in items:
                    label = status
                    if status == "LOW STOCK":
                        label = "LOW STOCK !"
                    elif status == "OUT OF STOCK":
                        label = "OUT OF STOCK !!"

                    print(f"{p.sku} | {p.name} | Qty: {p.quantity} | £{p.price} | {p.category} | {label}")

                print("\n--- Add Favourite Products ---")
                favourite_prompt(favourite_service)

        elif choice == "2":
            query = input("Please search up desired product by SKU / Name / Description : ")
            results = product_service.search_products(query)

            if not results:
                print("No matching products found.")
            else:
                print("\n--- Search Results ---")
                for p in results:
                    print(f"{p.sku} | {p.name} | {p.description} | Qty: {p.quantity} | £{p.price} | {p.category}")

                print("\n--- Add Favourite Products ---")
                favourite_prompt(favourite_service)

        elif choice == "3":
            category = input("Category (leave blank for all categories): ").strip()
            max_qty = input("Max quantity (leave blank for no limit): ").strip()
            sort_by = input("Sort by [name/quantity/price] (leave blank for none): ").strip().lower()

            if sort_by == "":
                sort_by = None
            if category == "":
                category = None
            if max_qty == "":
                max_qty = None

            results = product_service.filter_products(category=category, max_qty=max_qty, sort_by=sort_by)

            if not results:
                print("No products match that filter.")
            else:
                print("\n--- Filtered Products ---")
                for p in results:
                    print(f"{p.sku} | {p.name} | {p.description} | Qty: {p.quantity} | £{p.price} | {p.category}")

                print("\n--- Add Favourite Products ---")
                favourite_prompt(favourite_service)


        elif choice == "4":
            add_product_menu(product_service)
        elif choice == "5":
            remove_product_menu(product_service)
        elif choice == "6":
            update_product_menu(product_service)
        elif choice == "7":
            low_stock_alerts_menu(product_service, low_stock_threshold)
        elif choice == "8":
            favourite_products, error_message = favourite_service.get_favourites()
            if error_message is not None:
                print(error_message)
            elif not favourite_products:
                print("No favourites yet.")
            else:
                print("\n--- Favourite Products ---")
                for p in favourite_products:
                    print(
                        f"{p.sku} | {p.name} | {p.description} | Qty: {p.quantity} | £{p.price} | {p.category}")

                print("\n--- Add and Remove Favourite Products ---")
                favourite_prompt(favourite_service)

                while True:
                    sku = input("\nEnter SKU to unfavourite (or press Enter to go back): ").strip()
                    if sku == "":
                        break
                    print(favourite_service.unfavourite_product(sku))
        elif choice == "9":
            # The ONLY place user changes threshold
            low_stock_threshold = set_low_stock_threshold(low_stock_threshold)

        elif choice == "10":
            print("\n----------[ DEACTIVATE AND REACTIVATE PRODUCTS1 ]----------")
            print("\n1) Deactivate product")
            print("2) Reactivate product")
            print("0) Cancel")

            action = input("Choose an option: ").strip()

            if action == "1":
                sku = input("Enter SKU to deactivate: ").strip()
                result = product_service.deactivate_product(sku)
                print(result)

            elif action == "2":
                sku = input("Enter SKU to reactivate: ").strip()
                result = product_service.reactivate_product(sku)
                print(result)

            elif action == "0":
                print("Action cancelled.")

            else:
                print("Invalid option.")




        elif choice == "0":
            return low_stock_threshold
        else:
            print("Invalid choice. Try again.")


def purchase_orders_menu(menus, auth_service, purchase_order_service):
    while True:
        choice = menus.view_purchase_orders_menu()

        if choice == "1":
            if auth_service.current_user is None:
                print("Authorisation failed. Please login first.")
                menus.auth_menu(auth_service)
                continue


            expected_date = input("Expected delivery date (YYYY-MM-DD): ").strip()

            try:
                count = int(input("How many product lines? ").strip())
            except ValueError:
                print(" Invalid number entered.")
                continue

            lines = []
            for i in range(count):
                print(f"\nLine {i+1}")
                sku = input("SKU: ").strip()
                try:
                    qty = int(input("Quantity: ").strip())
                except ValueError:
                    print("Quantity must be a number. Line skipped.")
                    continue

                lines.append({"sku": sku, "quantity": qty})


            created_by = auth_service.current_user.username

            purchase_order_service.create_purchase_order(
          expected_date, lines, created_by
            )

        elif choice == "2":
            orders = purchase_order_service.get_purchase_order()

            if not orders:
                print("No purchase orders found.")
            else:
                print("\n=== Purchase Orders ===")
                for po in orders:
                    print(f"{po.po_id} | ETA: {po.expected_date} | "
                          f"By: {po.created_by} | Status: {po.status}")
        elif choice == "3":
            po_id = input("Purchase Order ID: ").strip()
            print("Choose new status: CREATED / APPROVED / PARTIALLY_RECEIVED / COMPLETED / CANCELLED")
            new_status = input("New status: ").strip()

            user = auth_service.current_user.username
            result = purchase_order_service.update_po_status(po_id, new_status, user)
            print(result)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

def summary_dashboard_menu(product_service, low_stock_threshold):

    summary = product_service.get_dashboard_summary(low_stock_threshold)

    print("\n==============================")
    print("       [ DASHBOARD ]")
    print("==============================")
    print("Total products:", summary["total_products"])
    print("Total units in stock:", summary["total_units"])
    print("Low stock items (< " + str(summary["threshold"]) + "):", summary["low_stock_count"])
    print("System status:", summary["system_status"])
    print("Low stock %:", str(summary["low_stock_percent"]) + "%")
    print("Out of stock %:", str(summary["out_of_stock_percent"]) + "%")
    print("==============================\n")
    input("Press Enter to go back...")

def returns_menu(return_service):
    print("\n----------[ RETURNS ]----------")
    print("Accepted conditions for restock: sealed, unopened, resellable")
    print("Press Enter on SKU to go back.\n")

    while True:
        sku = input("Enter SKU to return (or press Enter to go back): ").strip()
        if sku == "":
            break

        qty = input("Enter quantity: ").strip()
        condition = input("Enter condition (sealed/unopened/resellable/damaged/used): ").strip()

        result = return_service.process_return(sku, qty, condition)
        print(result)

def budget_menu(menus, budget_service):
    while True:
        choice = menus.view_budget_menu()

        if choice == "1":
            print(budget_service.view_monthly_budget())
        elif choice == "2":
            amount = input(" Enter monthly budget amount for restocking : ").strip()
            print(budget_service.set_monthly_budget(amount))
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")



def main():
    menus = Menus()
    user_repo = UserRepo("users.txt")
    stock_repo = StockRepo("stocks.txt")
    product_repo = ProductRepo("products.txt")
    favourite_repo = FavouriteRepo("favourites.txt")
    return_repo = ReturnRepo("returns.txt")

    auth_service = AuthService(user_repo)
    category_repo = None
    product_service = ProductService(product_repo, category_repo)
    stock_service = StockService(product_repo)
    favourite_service = FavouriteService(favourite_repo, product_repo, auth_service)
    return_service = ReturnService(product_repo, stock_service, return_repo)
    budget_repo = BudgetRepo("budgets.txt")
    budget_service = BudgetService(budget_repo)

    purchase_order_service = PurchaseOrderService()

    menus.auth_menu(auth_service)
    low_stock_threshold = 5

    while True:
        choice = menus.view_main_menu()

        if choice == "1":
            low_stock_threshold = products_menu(
                menus, product_service, favourite_service, auth_service, low_stock_threshold
            )
        elif choice == "2":
            if auth_service.current_user is None:
                print("Authorization failed. Please login first.")
                menus.auth_menu(auth_service)
            else:
                stock_menu(menus, auth_service, stock_service)
        elif choice == "3":
            purchase_orders_menu(menus, auth_service, purchase_order_service)
        elif choice == "4":
            auth_service.logout()
            print("Logged out successfully.")
            menus.auth_menu(auth_service)
        elif choice == "5":
            summary_dashboard_menu(product_service, low_stock_threshold)
        elif choice == "6":
            returns_menu(return_service)
        elif choice== "7":
            budget_menu(menus,budget_service)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()









