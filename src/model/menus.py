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
        print("0) Back")
        return input("Choose an option: ").strip()

    def view_stock_menu(self):
        print("\n------------[ STOCK ]-----------")
        print("1) Record stock increase")
        print("2) Record stock decrease")
        print("0) Back")
        return input("Choose an option: ").strip()





def auth_menu(auth_service):
    pass

def stock_menu(auth_service,stock_service):
    pass