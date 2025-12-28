class FavouriteService:
    def __init__(self, favourite_repo, product_repo, auth_service):
        self.favourite_repo = favourite_repo
        self.product_repo = product_repo
        self.auth_service = auth_service

    def _get_username(self):

        if self.auth_service is None:
            return None
        if self.auth_service.current_user is None:
            return None
        return self.auth_service.current_user.username

    def favourite_product(self, sku):
        username = self._get_username()
        if username is None:
            return "You must be logged in to favourite products."

        sku = sku.strip()
        if sku == "":
            return "SKU cannot be empty."

        product = self.product_repo.find_by_sku(sku)
        if product is None:
            return "Product not found."

        if self.favourite_repo.is_favourite(username, sku):
            return "This product is already favourited."

        self.favourite_repo.add_favourite(username, sku)
        return "Product added to favourites."

    def get_favourites(self):
        username = self._get_username()
        if username is None:
            return None, "You must be logged in to view favourites."

        skus = self.favourite_repo.get_favourites(username)

        products = []
        for sku in skus:
            product = self.product_repo.find_by_sku(sku)
            if product is not None:
                products.append(product)

        return products, None
