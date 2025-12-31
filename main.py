from model.menus import Menus
from Repo.product_repo import ProductRepo
from Service.product_service import ProductService
from Repo.user_repo import UserRepo
from Repo.stock_repo import StockRepo
from Service.auth_service import AuthService
from Service.stock_service import StockService
from Service.purchase_order_service import PurchaseOrderService


def stock_menu(menus, auth_service, stock_service):
    while True:
        choice = menus.view_stock_menu()

        if choice == "1":
            print("TODO later: Record stock increase")
        elif choice == "2":
            print("TODO later: Record stock decrease")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def add_product_menu(product_service):
    sku = input("Enter SKU: ")
    name = input("Enter name: ")
    description = input("Enter description: ")
    quantity = input("Enter quantity: ")
    price = input("Enter price: ")
    category = input("Enter category (optional): ")

    if category == "":
        category = None

    result = product_service.add_new_product(sku, name, description, quantity, price, category)
    print(result)


def remove_product_menu(product_service):
    sku = input("Enter SKU to remove: ").strip()
    result = product_service.remove_product(sku)
    print(result)


def products_menu(menus, product_service):
    while True:
        choice = menus.view_products_menu()

        if choice == "1":
            print("TODO later: view products")
        elif choice == "2":
            print("TODO later: Search products")
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


        elif choice == "4":
            add_product_menu(product_service)
        elif choice == "5":
            remove_product_menu(product_service)
        elif choice == "0":
            break
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
                    print(f"{po.po_id} | Supplier: {po.supplier_id} | ETA: {po.expected_date} | "
                          f"By: {po.created_by} | Status: {po.status}")

        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def main():
    menus = Menus()
    user_repo = UserRepo("users.txt")
    stock_repo = StockRepo("stocks.txt")
    product_repo = ProductRepo("products.txt")
    product_service = ProductService(product_repo, None)


    auth_service = AuthService(user_repo)
    stock_service = StockService(stock_repo)

    purchase_order_service = PurchaseOrderService()

    menus.auth_menu(auth_service)

    while True:
        choice = menus.view_main_menu()

        if choice == "1":
            products_menu(menus, product_service)
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

        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
