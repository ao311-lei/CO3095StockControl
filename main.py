from user_repo import UserRepo
from stock_repo import StockRep
from auth_service import AuthService
from stock_service import StockService
from menus import auth_menu, stock_menu

def main():
    user_repo = UserRepository("users.txt")
    stock_repo = StockRepository("stock.txt")
    auth_service = AuthService(user_repo)
    stock_service = StockService(stock_repo)
    auth_menu(auth_service)
    if auth_service.current_user is not None:
        stock_menu(auth_service, stock_service)

if __name__ == '__main__':
    main()
