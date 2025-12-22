from user_repo import UserRepo
from stock_repo import StockRep
from auth_service import AuthService
from stock_service import StockService
from menus import auth_menu, stock_menu

from Repo.product_repo import ProductRepo
from Service.product_service import ProductService


def main():
    user_repo = UserRepository("users.txt")
    stock_repo = StockRepository("stock.txt")
    auth_service = AuthService(user_repo)
    stock_service = StockService(stock_repo)
    auth_menu(auth_service)
    if auth_service.current_user is not None:
        stock_menu(auth_service, stock_service)
    product_repo = ProductRepo("products.txt")
    product_service = ProductService(product_repo, None)

def add_product_menu(product_service):
    sku = input("Enter SKU: ")
    name = input("Enter name: ")
    description = input("Enter description: ")
    quantity = input("Enter quantity: ")
    price = input("Enter price: ")
    category = input("Enter category (optional): ")

    if category == "":
        category = None

    result = product_service.add_new_product(sku, name, description, quantity, price, category)
    print(result)

if __name__ == '__main__':
    main()
