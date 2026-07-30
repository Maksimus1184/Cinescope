import pytest
import allure
import datetime
from pytest_check import check
from api.api_manager import ApiManager
from models.base_models import TestUser, LoginRequest, LoginResponse, ErrorResponse, RegisterUserResponse
from enums.enums import Roles


class TestAuthAPI:

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    @pytest.mark.slow
    def test_register_user(self, api_manager: ApiManager, test_user: TestUser):
        """
        Тест на регистрацию пользователя.
        Отправляем только необходимые поля для регистрации.
        """
        # Подготавливаем данные для регистрации (только нужные поля)
        user_data = {
            "email": test_user.email,
            "fullName": test_user.fullName,
            "password": test_user.password,
            "passwordRepeat": test_user.passwordRepeat,
            "roles": test_user.roles
        }

        response = api_manager.auth_api.register_user(user_data=user_data)
        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.email == test_user.email, "Email не совпадает"
        assert register_user_response.fullName == test_user.fullName, "FullName не совпадает"

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_register_and_login_user(self, api_manager: ApiManager, registered_user: TestUser):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = LoginRequest(
            email=registered_user.email,
            password=registered_user.password
        )

        response = api_manager.auth_api.login_user(login_data)
        login_response = LoginResponse(**response.json())

        assert login_response.accessToken is not None, "Токен доступа отсутствует в ответе"
        assert login_response.user["email"] == registered_user.email, "Email не совпадает"

    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.integration
    def test_negative_email_auth_user(self, api_manager: ApiManager, registered_user: TestUser):
        """Тест с неверным email."""
        login_data = LoginRequest(
            email="wrong_email@mail.ru",
            password=registered_user.password
        )

        response = api_manager.auth_api.login_user(login_data, expected_status=[401, 500])
        error_response = ErrorResponse(**response.json())

        assert error_response.statusCode in (401, 500)
        assert error_response.message == "Неверный логин или пароль"
        assert error_response.error == "Unauthorized"

    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.integration
    def test_negative_password_auth_user(self, api_manager: ApiManager, registered_user: TestUser):
        """Тест с неверным паролем."""
        login_data = LoginRequest(
            email=registered_user.email,
            password="WrongPassword123"
        )
        response = api_manager.auth_api.login_user(login_data, expected_status=[401])
        error_response = ErrorResponse(**response.json())

        assert error_response.statusCode == 401
        assert error_response.message == "Неверный логин или пароль"
        assert error_response.error == "Unauthorized"

    @pytest.mark.api
    @pytest.mark.regression
    @pytest.mark.integration
    def test_negative_no_body_auth_user(self, api_manager: ApiManager):
        """Тест с пустым телом запроса."""
        login_data = {}
        response = api_manager.auth_api.login_user(login_data, expected_status=[400, 401])

        # Проверяем наличие ошибки в ответе
        response_json = response.json()
        assert "message" in response_json or "error" in response_json, "Нет сообщения об ошибке"

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: TestUser, mocker):
        with allure.step("Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(
                id="mock_id_123",
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
            user_data = {
                "email": test_user.email,
                "fullName": test_user.fullName,
                "password": test_user.password,
                "passwordRepeat": test_user.passwordRepeat,
                "roles": test_user.roles
            }
            register_user_response = api_manager.auth_api.register_user(user_data)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):
                with check:
                    check.equal(
                        register_user_response.fullName,
                        mock_response.fullName,
                        "НЕСОВПАДЕНИЕ fullName"
                    )
                    check.equal(
                        register_user_response.email,
                        mock_response.email,
                        "НЕСОВПАДЕНИЕ email"
                    )

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):
                    check.equal(
                        register_user_response.banned,
                        mock_response.banned,
                        "НЕСОВПАДЕНИЕ banned"
                    )

            with allure.step("Проверка поля verified"):
                with check:
                    check.equal(
                        register_user_response.verified,
                        mock_response.verified,
                        "НЕСОВПАДЕНИЕ verified"
                    )