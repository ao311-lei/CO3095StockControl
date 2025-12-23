class Menus:
    def view_main_menu(self):
        print("\n==============================")
        print("     [ STOCK CONTROL SYSTEM ]   ")
        print("==============================")
        print("1) Products")
        print("2) Stock")
        print("3) Account")
        print("0) Exit")
        return input("Choose an option: ").strip()

    def view_products_menu(self):
        print("\n----------[ PRODUCTS ]----------")
        print("1) View all products")
        print("2) Search products")
        print("3) Filter products")
        print("4) Add Product")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_stock_menu(self):
        print("\n------------[ STOCK ]-----------")
        print("1) Record stock increase")
        print("2) Record stock decrease")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_account_menu(self):
        print("\n-----------[ ACCOUNT ]----------")
        print("1) Login")
        print("2) Sign up")
        print("0) Back")
        return input("Choose an option: ").strip()

def category_menu(category_service):
    print("\n----------[ CATEGORIES ]----------")
    print("1. Create category")
    print("2. Rename category")
    print("3. Deactivate category")
    print("4. List categories")
    print("5. Back")

    choice = input("Choose option: ")

    try:
        if choice == "1":
            cid = input("Category ID: ")
            name = input("Category name: ")
            category_service.create_category(cid, name)
            print("Category created successfully")

        elif choice == "2":
            cid = input("Category ID: ")
            new_name = input("New category name: ")
            category_service.rename_category(cid, new_name)
            print("Category renamed successfully")

        elif choice == "3":
            cid = input("Category ID: ")
            category_service.deactivate_category(cid)
            print("Category deactivated successfully")

        elif choice == "4":
            categories = category_service.list_categories()
            for c in categories:
                status = "Active" if c.active else "Inactive"
                print(c.category_id, "-", c.name, "-", status)

        elif choice == "5":
            # Exit the category menu
            break

        else:
            print("Invalid option")

    except ValueError as e:
        # Catch and display validation errors
        print("Error:", e)


def auth_menu(auth_service):
    pass

def stock_menu(auth_service,stock_service):
    pass