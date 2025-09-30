import pytest
import requests
import logging  # <-- Импортируем logging
import json  # <-- Если используете json=, лучше импортировать


class CustomRequester:
    """
    Кастомный реквестер для стандартизации и упрощения отправки HTTP-запросов.
    """
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()  # Можно добавить эти заголовки в сессию здесь
        self.session.headers.update(self.headers)  # Например, если вы хотите, чтобы они были всегда
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # Убедитесь, что логгер настроен, если хотите видеть вывод логов
        # logging.basicConfig()

    def log_request_and_response(self, response):
        """Логирует информацию о запросе и ответе."""
        self.logger.info(f"Request: {response.request.method} {response.request.url}")
        self.logger.info(f"Request Headers: {response.request.headers}")
        if response.request.body:
            self.logger.info(f"Request Body: {response.request.body}")
        self.logger.info(f"Response Status: {response.status_code}")
        self.logger.info(f"Response Headers: {response.headers}")

        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        try:
            # Если ответ содержит JSON, логируем его
            if response.content and len(response.content) > 0:  # Проверяем, есть ли вообще контент
                self.logger.info(f"Response Body (JSON): {response.json()}")
            else:
                self.logger.info("Response Body: (пусто)")
        except json.JSONDecodeError:
            # Если не удалось распарсить JSON, логируем как обычный текст
            self.logger.info(f"Response Body (Text): {response.text}")
        except Exception as e:
            # Для перехвата любых других неожиданных ошибок при логировании
            self.logger.error(f"Ошибка при попытке логировать тело ответа: {e}. Тело: {response.text}")

    # Исправленный метод send_request
    def send_request(self, method, endpoint, json=None, data=None, expected_status=None, need_logging=True,
                     headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            current_headers = self.session.headers.copy()
            if headers:
                current_headers.update(headers)

            if need_logging:
                self.logger.info(f"Запрос: {method} {url}")
                self.logger.info(f"  Заголовки: {current_headers}")
                if json: self.logger.info(f"  JSON: {json}")
                elif data: self.logger.info(f"  Data: {data}")

            response_obj = self.session.request(
                method=method,
                url=url,
                json=json,
                data=data,
                headers=current_headers
            )

            # --- Проверка ожидаемого статуса ---
            # Если expected_status указан, и он не совпадает, вызываем pytest.fail.
            # Это гарантирует, что мы работаем с объектом response_obj, если тест не упал.
            if expected_status is not None:
                if response_obj.status_code != expected_status:
                    error_message = f"Запрос к {method} {url} вернул статус {response_obj.status_code}, ожидался {expected_status}. Ответ: {response_obj.text}"
                    self.logger.error(error_message)
                    pytest.fail(error_message)

            # Логирование (если нужно)
            if need_logging:
                self.log_request_and_response(response_obj)

            # --- ВСЕГДА возвращаем объект Response, если не вызван pytest.fail ---
            return response_obj

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Ошибка сети при запросе к {method} {url}: {e}")
        except AssertionError as e:
            pytest.fail(f"Ошибка проверки статуса: {e}")