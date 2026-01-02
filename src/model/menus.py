
class Menus:
    def view_main_menu(self, current_user):
        print("\n==============================")
        print("     [ STOCK CONTROL SYSTEM ]   ")
        print("==============================")
        print("1) Products")
        if current_user and current_user.is_manager():
            print("2) Stock")
            print("3) Purchase Orders")
        print("4) Account")
        print("5) Dashboard")
        print("6) Returns")
        if current_user and current_user.is_manager():
            print("2) Stock")
            print("3) Purchase Orders")
            print("7) Budget")
            print("8) Suppliers")
            print("9) Reservations")
        print("0) Exit")
        return input("Choose an option: ").strip()

    def view_products_menu(self, current_user):
        print("\n----------[ PRODUCTS ]----------")
        print("1) View all products")
        print("2) Search products")
        print("3) Filter products")
        print("8) View favourite products")
        print("0) Back")
        if current_user and current_user.is_manager():
            print("4) Add Product")
            print("5) Remove Product")
            print("6) Update Product")
            print("7) Low Stock Alerts")
            print("9) Set Low Stock Threshold")
        if current_user and current_user.is_admin():
            print("10) Deactivate and reactivate products")
        return input("Choose an option: ").strip()

    def view_stock_menu(self):
        print("\n------------[ STOCK ]-----------")
        print("1) Record stock increase")
        print("2) Record stock decrease")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_budget_menu(self):
        print("\n-----------[ BUDGET ]----------")
        print("1) View current budget")
        print("2) Set / update budget")
        print("3) Estimate product restock cost ")
        print("0) Back")
        return input("Choose an option: ").strip()

    def auth_menu(self, auth_service,activity_service):
        while True:
            print("\n-----------[ ACCOUNT ]----------")

            if auth_service.current_user is None:
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
                    return
                else:
                    print("Invalid option")
                continue

            user = auth_service.current_user
            print(f"Logged in as: {user.username} ({user.role})")
            print("1) Logout")

        # Admin-only option
            if user.role == "ADMIN":
                print("2) Assign roles")
                print("3) View activity stats")

            print("0) Back")
            choice = input("Choose option: ").strip()

            if choice == "1":
                auth_service.logout()
                print("Logged out.")
                return
            elif choice == "2" and user.role == "ADMIN":
                return "ASSIGN_ROLES"
            elif choice == "3" and user.role == "ADMIN":
                return "VIEW_ACTIVITIES"
            elif choice == "0":
                return
            else:
                print("Invalid option")

    def view_purchase_orders_menu(self):
        print("\n----------[ PURCHASE ORDERS ]----------")
        print("1) Create purchase order")
        print("2) View purchase orders")
        print("3) Update purchase orders")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_suppliers_menu(self):
        print("\n---------[ SUPPLIERS ]---------")
        print("1) Create supplier")
        print("2) Update supplier")
        print("3) Deactivate supplier")
        print("4) List suppliers")
        print("5) Supplier product catalogue")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_reservations_menu(self):
        print("\n----------[ RESERVATIONS ]----------")
        print("1) Create reservation")
        print("2) View reservations")
        print("3) Cancel reservation")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_supplier_catalogue_menu(self):
        print("\n----[ SUPPLIER PRODUCT CATALOGUE ]----")
        print("1) Link product to supplier")
        print("2) Unlink product from supplier")
        print("3) View supplier catalogue")
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_assign_roles(self):
        print("\n----------[ ASSIGN ROLE ]----------")
        print("1) Update role")

    def view_admin_activity(auth_service):
        print("\n----------[ ACTIVITY ]----------")
        print("1) View activity stats: 24hrs")
        print("2) View activity stats: 7 days")
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


def auth_menu(auth_service):
    pass


def stock_menu(auth_service, stock_service):
    pass
