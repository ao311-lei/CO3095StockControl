from Repo.product_repo import ProductRepo
from Service.product_service import ProductService


def main():
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
