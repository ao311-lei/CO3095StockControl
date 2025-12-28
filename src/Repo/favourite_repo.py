class FavouriteRepo:

    def __init__(self, filename="favourites.txt"):
        self.filename = filename
        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def load_all(self):
        favourites = []
        with open(self.filename, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    username, sku = line.split(",", 1)
                    favourites.append((username.strip(), sku.strip()))
        return favourites

    def save_all(self, favourites):
        with open(self.filename, "w") as file:
            for username, sku in favourites:
                file.write(f"{username},{sku}\n")

    def is_favourite(self, username, sku):
        if (username, sku) in self.load_all():
            return True
        else:
            return False

    def add_favourite(self, username, sku):
        favourites = self.load_all()
        if (username, sku) not in favourites:
            favourites.append((username, sku))
            self.save_all(favourites)

    def get_favourites(self, username):
        favourites = []
        for u, sku in self.load_all():
            if u == username:
                favourites.append(sku)
        return favourites

