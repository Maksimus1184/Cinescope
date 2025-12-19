from api.api_manager import ApiManager

class User:
    def __init__(self, email: str, password: str, roles: list, api: ApiManager):
        self.email = email
        self.password = password
        self.roles = roles
        self.api = api

    @property
    def creds(self):
        """Возвращает кортеж (email, password)"""
        return self.email, self.password

    def get_creds_dict(self):
        """Возвращает креды в виде словаря для API"""
        return {
            "email": self.email,
            "password": self.password
        }