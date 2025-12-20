class AuthService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
        self.current_user = None

    def sign_up(self, username, password, role = "staff"):
        pass

    def login(self, username, password):
        pass

    def logout(self):
        pass