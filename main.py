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



