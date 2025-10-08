from api.auth_api import AuthAPI # Убедитесь, что импорт правильный
from api.user_api import UserAPI # Убедитесь, что импорт правильный
from constants import BASE_URL

class ApiManager:
    def __init__(self, session):
        self.session = session
        # !!! ApiManager ДОЛЖЕН передавать session И base_url !!!
        self.auth_api = AuthAPI(session=session, base_url=BASE_URL)
        self.user_api = UserAPI(session=session, base_url=BASE_URL)
