from custom_requester.custom_requester import CustomRequester
from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT
import pytest

class AuthAPI(CustomRequester):
    def __init__(self, session, base_url): # <-- ДОЛЖЕН ПРИНИМАТЬ base_url
        super().__init__(session=session, base_url=base_url)
        self.session = session

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            json=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=[200, 201]):
        response = self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            json=login_data,
            expected_status=None  # не проверяем статус внутри send_request
        )
        if expected_status is not None and response.status_code not in expected_status:
            # тогда ошибка
            error_message = f"Запрос на логин вернул статус {response.status_code}, ожидался {expected_status}. Ответ: {response.text}"
            self.logger.error(error_message)
            pytest.fail(error_message)
        return response

    def authenticate(self, user_creds):
        """
        Авторизует пользователя и устанавливает токен авторизации в сессии.
        """
        login_data = {
            "email": user_creds["email"],
            "password": user_creds["password"]
        }

        try:
            # send_request уже проверяет статус и логирует ошибки
            response_obj = self.login_user(login_data)
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