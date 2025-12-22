from model.menus import Menus


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

def products_menu(menus, product_service):
    while True:
        choice = menus.view_products_menu()

        if choice == "1":
            print("TODO later: View all products")
        elif choice == "2":
            print("TODO later: Search products")
        elif choice == "3":
            print("TODO later: Filter products")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

def main():

    menus = Menus()

    # Service placeholders
    # These will later be replaced with real service objects in other user stories and sprints
    auth_service = None
    stock_service = None
    product_service = None

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









