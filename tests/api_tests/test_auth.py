from dbm.sqlite3 import error

from api.api_manager import ApiManager
from models.base_models import RegisterUserResponse
import  pytest
from models.base_models import TestUser, LoginRequest, LoginResponse, ErrorResponse


class TestAuthAPI:
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    @pytest.mark.slow
    def test_register_user(self, api_manager: ApiManager, test_user: TestUser):
        """
        Тест на регистрацию пользователя.
        """
        # Передаем объект TestUser напрямую, без model_dump
        response = api_manager.auth_api.register_user(user_data=test_user)

        # Создаем объект RegisterUserResponse из ответа API
        register_user_response = RegisterUserResponse(**response.json())

        # Проверки - сравниваем с атрибутами объекта TestUser
        assert register_user_response.email == test_user.email, "Email не совпадает"

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_register_and_login_user(self, api_manager: ApiManager, registered_user: TestUser):
        """
        Тест на регистрацию и авторизацию пользователя.
        Использует зарегистрированного пользователя как объект TestUser.
        """
        # Создаем объект LoginRequest из данных зарегистрированного пользователя
        login_data = LoginRequest(
            email=registered_user.email,
            password=registered_user.password
        )

        # Передаем объект LoginRequest напрямую
        response = api_manager.auth_api.login_user(login_data)

        # Создаем объект LoginResponse из ответа API (а не RegisterUserResponse)
        login_response = LoginResponse(**response.json())

        # Проверки
        assert login_response.accessToken is not None, "Токен доступа отсутствует в ответе"
        assert login_response.user["email"] == registered_user.email, "Email не совпадает"

    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.integration
    def test_negative_email_auth_user(self, api_manager: ApiManager, registered_user: TestUser):
        """Тест на регистрацию и авторизацию пользователя c неверным email."""
        login_data = LoginRequest(
            email="Maksimus123456789@mail.ru",
            password=registered_user.password
        )

        response = api_manager.auth_api.login_user(login_data, expected_status=[401, 500])

        # Используем ErrorResponse для ошибки
        error_response = ErrorResponse(**response.json())

        # Проверки
        assert error_response.statusCode in (401, 500)
        assert error_response.message == "Неверный логин или пароль"
        assert error_response.error == "Unauthorized"


    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.integration
    def test_negative_password_auth_user(self, api_manager: ApiManager, registered_user: TestUser):
        """Тест на регистрацию и авторизацию пользователя c неверным password."""
        login_data = LoginRequest(
            email = registered_user.email,
            password = "Password1234"
        )
        response = api_manager.auth_api.login_user(login_data, expected_status=[401])

        # Используем ErrorResponse для ошибки
        error_response = ErrorResponse(**response.json())

        print(error_response.statusCode)
        # Проверки
        assert error_response.statusCode in [401]
        assert error_response.message == "Неверный логин или пароль"
        assert error_response.error == "Unauthorized"

    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.integration
    def test_negative_no_body_auth_user(self, api_manager: ApiManager, registered_user: TestUser):
        """Тест на регистрацию и авторизацию пользователя c пустым телом запроса."""
        login_data = {}
        response = api_manager.auth_api.login_user(login_data, expected_status=[401])

        # Используем ErrorResponse для ошибки
        error_response = ErrorResponse(**response.json())

        # Проверки
        assert error_response.statusCode in [401]
        assert error_response.message == "Неверный логин или пароль"
        assert error_response.error == "Unauthorized"

