class Menus:
    def view_main_menu(self):
        print("\n==============================")
        print("    [ STOCK CONTROL SYSTEM ]   ")
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

    def auth_menu(self,auth_service):
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
                break

            else:
                print("Invalid option")



def stock_menu(auth_service, stock_service):
    pass
