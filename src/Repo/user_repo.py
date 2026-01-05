from model.user import User
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
                line = line.strip()
                if not line:
                    continue

                parts = line.split(":")
                username = parts[0].strip()
                password = parts[1].strip()
                role = parts[2].strip().upper() if len(parts) > 2 and parts[2].strip() else "STAFF"
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

    def save_all_users(self, users):
        with open(self.filename, "w") as file:
            for user in users:
                file.write(user.username + ":" + user.password + ":" + user.role + "\n")

    def update_role(self, username, new_role):
        users = self.load_users()
        new_role = new_role.strip().upper()

        if new_role not in ("STAFF", "ADMIN", "MANAGER"):
            raise ValueError("Invalid role")

        for user in users:
            if user.username == username:
                user.role = new_role
                self.save_all_users(users)
                return True
        return False
