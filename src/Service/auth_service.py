import hashlib
from model.user import User

class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.current_user = None

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def sign_up(self, username, password, role="staff"):
        if username.strip() == "":
            raise ValueError("Username cannot be empty")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        existing_user = self.user_repo.get_user(username)
        if existing_user is not None:
            raise ValueError("Username already exists")

        password = self._hash_password(password)

        user = User(username, password, role)

        self.user_repo.save_user(user)

        return True

    def login(self, username, password):
        user = self.user_repo.get_user(username)
        if user is None:
            return None

        password = self._hash_password(password)

        if password != user.password:
            return False

        self.current_user = user
        return True

    def assign_role(self, target_username, new_role):
        if self.current_user is None:
            print("You must be logged in")
            return False

        if getattr(self.current_user, "role", "").upper() != "ADMIN":
            print("Access denied: Admin role must be 'ADMIN'")
            return False

        new_role = new_role.strip().upper()
        if new_role not in ["ADMIN", "STAFF","MANAGER"]:
            print("Invalid role. Choose 'ADMIN', 'STAFF' or 'MANAGER'")
            return False

        if target_username == self.current_user.username:
            print("You can't change your own role")
            return False

        updated = self.user_repo.update_user(target_username, new_role)
        if not updated:
            print("User not found")
            return False

        print("You have successfully changed your role")
        return True

    def logout(self):
        self.current_user = None
        return True
