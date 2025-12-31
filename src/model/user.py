class User:
    def __init__(self,username,password, role = "STAFF"):
        self.username = username
        self.password = password
        self.role = role.upper()

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_manager(self):
        return self.role in ("MANAGER", "STAFF")