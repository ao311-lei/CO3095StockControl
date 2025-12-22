from Repo.user_repo import UserRepo
from Repo.stock_repo import StockRepo
from Service.auth_service import AuthService
from Service.stock_service import StockService


def main():
    user_repo = UserRepo("users.txt")
    stock_repo = StockRepo("stock.txt")
    auth_service = AuthService(user_repo)
    stock_service = StockService(stock_repo)


if __name__ == '__main__':
    main()
