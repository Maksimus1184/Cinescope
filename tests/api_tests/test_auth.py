from dbm.sqlite3 import error
import allure
from enums.enums import Roles
from api.api_manager import ApiManager
from models.base_models import RegisterUserResponse
import  pytest
from models.base_models import TestUser, LoginRequest, LoginResponse, ErrorResponse
import datetime
from pytest_check import check


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

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
        with allure.step(" Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(  # Фиктивный ответ
                id="id",
                email="email@email.com",
                fullName="fullName",
                verified=True,
                banned=False,
                roles=Roles.SUPER_ADMIN.value,
                createdAt=str(datetime.datetime.now())
            )

            mocker.patch.object(
                api_manager.auth_api,  # Объект, который нужно замокать
                'register_user',  # Метод, который нужно замокать
                return_value=mock_response  # Фиктивный ответ
            )

        with allure.step("Вызываем метод, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(test_user)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):  # обратите внимание на вложенность allure.step
                with check:
                    # Строка ниже выдаст исключение и но выполнение теста продолжится
                    check.equal(register_user_response.fullName, "INCORRECT_NAME", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response.email)

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):  # можно использовать вместо allure.step
                    check.equal(register_user_response.banned, mock_response.banned)

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
        with allure.step("Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(
                id="id",
                email="email@email.com",
                fullName="fullName",
                verified=True,
                banned=False,
                roles=Roles.SUPER_ADMIN.value,
                createdAt=str(datetime.datetime.now())
            )

            mocker.patch.object(
                api_manager.auth_api,
                'register_user',
                return_value=mock_response
            )

        with allure.step("Вызываем метод, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(test_user)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):
                with check:
                    # Теперь сравниваем с правильным значением
                    check.equal(
                        register_user_response.fullName,
                        mock_response.fullName,  # <-- ИСПРАВЛЕНО
                        "НЕСОВПАДЕНИЕ fullName"
                    )
                    check.equal(
                        register_user_response.email,
                        mock_response.email
                    )

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):
                    check.equal(
                        register_user_response.banned,
                        mock_response.banned
                    )

