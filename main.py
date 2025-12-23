from model.menus import Menus
from Repo.product_repo import ProductRepo
from Service.product_service import ProductService
from Repo.user_repo import UserRepo
from Repo.stock_repo import StockRepo
from Service.auth_service import AuthService
from Service.stock_service import StockService



def auth_menu(menus, auth_service):
    while True:
        choice = menus.view_account_menu()

        if choice == "1":
            print("TODO later: Login")
        elif choice == "2":
            print("TODO later: Sign up")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

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

def products_menu(menus, product_service):
    while True:
        choice = menus.view_products_menu()

        if choice == "1":
            print("TODO later: view products")
        elif choice == "2":
            query = input("Please search up desired product by SKU / Name / Description : ")
            results = product_service.search_products(query)

            if not results:
                print("No matching products found.")
            else:
                print("\n--- Search Results ---")
                for p in results:
                    print(f"{p.sku} | {p.name} | {p.description} | Qty: {p.quantity} | £{p.price} | {p.category}")

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
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def main():
    menus = Menus()

    user_repo = UserRepo("users.txt")
    stock_repo = StockRepo("stock.txt")
    auth_service = AuthService(user_repo)
    stock_service = StockService(stock_repo)

    # Must pass menus as first argument
    auth_menu(menus, auth_service)

    if auth_service.current_user is not None:
        stock_menu(menus, auth_service, stock_service)


    product_repo = ProductRepo("products.txt")
    product_service = ProductService(product_repo, None)


    # Main navigation loop
    while True:
        choice = menus.view_main_menu()

        if choice == "1":
            products_menu(menus, product_service)
        elif choice == "2":
            stock_menu(menus, auth_service, stock_service)
        elif choice == "3":
            auth_menu(menus, auth_service)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()









