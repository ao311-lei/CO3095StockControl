class Menus:
    def view_main_menu(self):
        print("\n==============================")
        print("     [ STOCK CONTROL SYSTEM ]   ")
        print("==============================")
        print("1) Products")
        print("2) Stock")
        print("3) Purchase Orders")
        print("4) Account")
        print("5) Dashboard")
        print("6) Returns")
        print("9) Reservations")
        print("0) Exit")
        return input("Choose an option: ").strip()

    def view_products_menu(self):
        print("\n----------[ PRODUCTS ]----------")
        print("1) View all products")
        print("2) Search products")
        print("3) Filter products")
        print("4) Add Product")
        print("5) Remove Product")
        print("6) Update Product")
        print("7) Low Stock Alerts")
        print("8) View favourite products")
        print("9) Set Low Stock Threshold")
        print("10) Deactivate and reactivate products")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_stock_menu(self):
        print("\n------------[ STOCK ]-----------")
        print("1) Record stock increase")
        print("2) Record stock decrease")
        print("0) Back")
        return input("Choose an option: ").strip()

    def auth_menu(self, auth_service):
        while True:
            print("\n-----------[ ACCOUNT ]----------")
            print("1. Login")
            print("2. Sign Up")
            print("3. Exit")

            choice = input("Choose option: ")

            if choice == "1":
                username = input("Username: ").strip()
                password = input("Password: ")

                if auth_service.login(username, password):
                    print("Login successful")
                    return
                else:
                    print("Invalid username or password")

            elif choice == "2":
                username = input("Choose username: ").strip()
                password = input("Choose password: ")

                try:
                    auth_service.sign_up(username, password)
                    print("Account created successfully")
                except ValueError as e:
                    print("Error:", e)

            elif choice == "3":
                print("bye")

            else:
                print("Invalid option")

    def view_purchase_orders_menu(purchase_orders_service):
        print("\n----------[ PURCHASE ORDERS ]----------")
        print("1) Create purchase order")
        print("2) View purchase orders")
        print("3) Update purchase orders")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_reservations_menu(reservation_service):
        print("\n----------[ RESERVATIONS ]----------")
        print("1) Create reservation")
        print("2) View reservations")
        print("3) Cancel reservation")
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
            print("Back")

        else:
            print("Invalid option")

    except ValueError as e:
        # Catch and display validation errors
        print("Error:", e)


    def view_reservation_menu(reservation_service):
        print("\n----------[ RESERVATIONS ]----------")
def auth_menu(auth_service):
    pass


def stock_menu(auth_service, stock_service):
    pass
