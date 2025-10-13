from .auth_api import AuthAPI
from .movies_api import MoviesAPI
from .user_api import UserAPI
from constants import BASE_URL, MOVIES_BASE_URL


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session=session, base_url=BASE_URL)
        self.user_api = UserAPI(session=session, base_url=BASE_URL)
        self.movies_api = MoviesAPI(session=session, base_url=MOVIES_BASE_URL)
