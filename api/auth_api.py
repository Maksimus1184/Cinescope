# api/auth_api.py
from custom_requester.custom_requester import CustomRequester
from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT
import pytest
from models.base_models import TestUser, LoginRequest


class AuthAPI(CustomRequester):
    def __init__(self, session, base_url):
        super().__init__(session=session, base_url=base_url)
        self.session = session

    def _prepare_data(self, data):
        """
        Подготовка данных для отправки.
        Если передан Pydantic объект - преобразуем в словарь.
        """
        if hasattr(data, 'model_dump'):
            # Это Pydantic модель
            return data.model_dump()
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError(f"Неподдерживаемый тип данных: {type(data)}")

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        Принимает либо объект TestUser, либо словарь.
        """
        # Подготавливаем данные
        if isinstance(user_data, TestUser):
            data = user_data.model_dump()
            # Удаляем поля, которые не нужны для регистрации
            fields_to_remove = ['id', 'verified', 'banned']
            for field in fields_to_remove:
                data.pop(field, None)
        else:
            data = self._prepare_data(user_data)

        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            json=data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=[200, 201]):
        """
        Авторизация пользователя.
        Принимает либо объект LoginRequest, либо словарь.
        """
        data = self._prepare_data(login_data)

        response = self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            json=data,
            expected_status=None  # не проверяем статус внутри send_request
        )

        # Проверяем статус вручную
        if expected_status is not None:
            if isinstance(expected_status, list):
                if response.status_code not in expected_status:
                    error_message = f"Запрос на логин вернул статус {response.status_code}, ожидался один из {expected_status}. Ответ: {response.text}"
                    self.logger.error(error_message)
                    pytest.fail(error_message)
            else:
                if response.status_code != expected_status:
                    error_message = f"Запрос на логин вернул статус {response.status_code}, ожидался {expected_status}. Ответ: {response.text}"
                    self.logger.error(error_message)
                    pytest.fail(error_message)

        return response

    def authenticate(self, user_creds):
        """
        Авторизует пользователя и устанавливает токен авторизации в сессии.
        Принимает либо объект LoginRequest, либо словарь с email и password.
        """
        # Если передан объект, преобразуем в словарь
        if hasattr(user_creds, 'model_dump'):
            login_data = user_creds.model_dump()
        elif isinstance(user_creds, dict):
            login_data = user_creds
        else:
            self.logger.error(f"Неподдерживаемый тип: {type(user_creds)}")
            return None

        try:
            # Отправляем запрос на логин
            response_obj = self.login_user(login_data, expected_status=[200, 201])
            response_data = response_obj.json()

            # Получаем токен
            token = response_data.get("accessToken")
            if not token:
                self.logger.error(f"Токен не найден в ответе. Ответ: {response_data}")
                return None

            # Обновляем заголовки сессии
            self._update_session_headers(**{"authorization": "Bearer " + token})
            self.logger.info("Токен получен и установлен в сессию")

            return token

        except Exception as e:
            self.logger.error(f"Ошибка при аутентификации: {e}")
            return None