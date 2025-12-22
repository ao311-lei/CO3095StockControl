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


def auth_menu(auth_service):
    pass

def stock_menu(auth_service,stock_service):
    pass