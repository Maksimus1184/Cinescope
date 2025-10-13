import json
import logging
import os

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
        self.headers = self.base_headers.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def send_request(self, method, endpoint, data=None, expected_status=200, need_logging=True):
        """
        Универсальный метод для отправки запросов.
        :param method: HTTP метод (GET, POST, PUT, DELETE и т.д.).
        :param endpoint: Эндпоинт (например, "/login").
        :param data: Тело запроса (JSON-данные).
        :param expected_status: Ожидаемый статус-код (по умолчанию 200).
        :param need_logging: Флаг для логирования (по умолчанию True).
        :return: Объект ответа requests.Response.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, json=data, headers=self.headers)
        if need_logging:
            self.log_request_and_response(response)
        if response.status_code != expected_status:
            raise ValueError(f"Unexpected status code: {response.status_code}. Expected: {expected_status}")
        return response

    def log_request_and_response(self, response):
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_data = response.text
            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not response.ok:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response.status_code}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response.status_code}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")


    def _update_session_headers(self, **kwargs): # **kwargs содержит {'authorization': 'Bearer token'}
        """
        Обновляет заголовки сессии, к которой принадлежит этот requester.
        """
        # Обновляем заголовки сессии, к которой этот requester имеет доступ
        if hasattr(self.session, 'headers'):
            # Просто добавляем новые заголовки из kwargs
            self.session.headers.update(kwargs)
            self.logger.info(f"Обновлены заголовки сессии: {kwargs}")
        else:
            self.logger.warning("Объект сессии не имеет атрибута 'headers'. Заголовки не обновлены.")

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
                     headers=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            current_headers = self.session.headers.copy()
            if headers:
                current_headers.update(headers)

            if need_logging:
                self.logger.info(f"Запрос: {method} {url}")
                self.logger.info(f"  Заголовки: {current_headers}")
                if json: self.logger.info(f"  JSON: {json}")
                if params: self.logger.info(f"  Параметры: {params}")
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

