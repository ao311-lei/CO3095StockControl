from user import User
class UserRepo:
    def __init__(self, filename):
        self.filename = filename

        try:
            open(self.filename, "r").close()
        except FileNotFoundError:
            open(self.filename, "w").close()

    def load_users(self):
        users = []
        with open(self.filename, "r") as file:
            for line in file:
                if line.strip():
                    username, password, role = line.strip().split(":")
                    users.append(User(username, password, role))

        return users


    def get_user(self, username):
        for user in self.load_users():
            if user.username == username:
                return user
            return None

    def save_user(self, user):
        if self.get_user(user.username) is not None:
            raise Exception("User already exists")

        with open(self.filename, "a") as file:
            file.write(user.username + ":" + user.password + ":" + user.role + "\n")