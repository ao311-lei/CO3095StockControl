from model.menus import Menus
from Repo.product_repo import ProductRepo
from Service.product_service import ProductService
from Repo.user_repo import UserRepo
from Repo.stock_repo import StockRepo
from Service.auth_service import AuthService
from Service.stock_service import StockService


def stock_menu(self, auth_service, stock_service):
    ...
    while True:
        choice = self.view_stock_menu()

        if choice == "1":
            sku = input("Enter SKU to increase stock: ").strip()
            amount_str = input("Enter amount to increase by: ").strip()

            try:
                amount = int(amount_str)
                new_qty = stock_service.record_stock_increase(sku, amount)
                print(f"Stock updated. New quantity for {sku}: {new_qty}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            sku = input("Enter SKU to decrease stock: ").strip()
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

def update_product_menu(product_service):
    sku = input("Enter SKU to update: ").strip()

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
        elif choice == "6":
            update_product_menu(product_service)
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

    # Service placeholders
    # These will later be replaced with real service objects in other user stories and sprints
    auth_service = AuthService(user_repo)
    stock_service = StockService(product_repo)

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









