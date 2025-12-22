import hashlib
from user import User

class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.current_user = None

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def sign_up(self, username, password, role= "staff"):
        if username.strip() == "":
            raise ValueError("Username cannot be empty")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if self.user_repo.user_exists(username) is not None:
            raise ValueError("Username already exists")


    def login(self, username, password):
        user = self.user_repo.find_by_username(username)
        if user is None:
            raise ValueError("User not found")

    def logout(self):
        pass
