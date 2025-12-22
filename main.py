from model.menus import Menus
from Repo.product_repo import ProductRepo
from Service.product_service import ProductService

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
            print("TODO later: Search products")
        elif choice == "3":
            print("TODO later: Filter products")
        elif choice == "4":
            add_product_menu(product_service)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def main():
    menus = Menus()

    product_repo = ProductRepo("products.txt")
    product_service = ProductService(product_repo, None)

    # Service placeholders
    # These will later be replaced with real service objects in other user stories and sprints
    auth_service = None
    stock_service = None


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









