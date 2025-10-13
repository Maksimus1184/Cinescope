
from custom_requester.custom_requester import CustomRequester
from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT

class AuthAPI(CustomRequester):
    def __init__(self, session, base_url): # <-- ДОЛЖЕН ПРИНИМАТЬ base_url
        super().__init__(session=session, base_url=base_url)
        self.session = session

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            json=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=201):
        """
        Авторизация пользователя.
        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            json=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        """
        Авторизует пользователя и устанавливает токен авторизации в сессии.
        :param user_creds: Словарь с кредами, например: {'email': '...', 'password': '...'}
        :return: Полученный токен авторизации (строка) или None в случае ошибки.
        """
        login_data = {
            "email": user_creds["email"],
            "password": user_creds["password"]
        }

        try:
            # Предполагаем, что login_user возвращает объект ответа, у которого есть .json()
            response_obj = self.login_user(login_data)
            response_data = response_obj.json()
        except AttributeError:  # Если login_user вернул None или не объект с .json()
            self.logger.error("login_user не вернул валидный объект ответа.")
            return None
        except Exception as e:  # Другие возможные ошибки при вызове login_user или .json()
            self.logger.error(
                f"Ошибка при вызове login_user или обработке ответа: {e}. Ответ: {response_obj.text if response_obj else 'No response object'}")
            return None

        token_key = "accessToken"
        if token_key not in response_data:
            error_message = f"Ключ '{token_key}' не найден в ответе API после логина. Ответ: {response_data}"
            self.logger.error(error_message)
            return None  # Возвращаем None, если токен отсутствует

        token = response_data[token_key]

        # Обновляем заголовки сессии
        self._update_session_headers(**{"authorization": "Bearer " + token})

        self.logger.info(f"Токен получен и установлен в сессию.")

        # --- ЯВНО ВОЗВРАЩАЕМ ТОКЕН ---
        return token