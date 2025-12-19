import json
import logging
import os

import pytest
import requests
from pydantic import BaseModel
from constants import RED, GREEN, RESET


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

    def log_request_and_response(self, response):
        """
        Логгирование запросов и ответов. Настройки логгирования описаны в pytest.ini
        Преобразует вывод в curl-like (-H хэдэеры), (-d тело)

        :param response: Объект response получаемый из метода "send_request"
        """
        try:
            request = response.request
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text
            if not is_success:
                self.logger.info(f"\tRESPONSE:"
                                 f"\nSTATUS_CODE: {RED}{response_status}{RESET}"
                                 f"\nDATA: {RED}{response_data}{RESET}")
        except Exception as e:
            self.logger.info(f"\nLogging went wrong: {type(e)} - {e}")

    def _update_session_headers(self, **kwargs):
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

    def send_request(self, method, endpoint, json=None, data=None, expected_status=None, need_logging=True,
                     headers=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            current_headers = self.session.headers.copy()
            if headers:
                current_headers.update(headers)
            if json is not None and isinstance(json, BaseModel):
                json = __import__('json').loads(json.model_dump_json())

            if data is not None and isinstance(data, BaseModel):
                data = __import__('json').loads(data.model_dump_json())
            if need_logging:
                self.logger.info(f"Запрос: {method} {url}")
                self.logger.info(f"  Заголовки: {current_headers}")
                if json:
                    self.logger.info(f"  JSON: {json}")
                if params:
                    self.logger.info(f"  Параметры: {params}")
                elif data:
                    self.logger.info(f"  Data: {data}")

            response_obj = self.session.request(
                method=method,
                url=url,
                json=json,
                data=data,
                headers=current_headers,
                params=params  # Добавьте params здесь
            )

            # --- Проверка ожидаемого статуса ---
            if expected_status is not None:
                # Если expected_status - список, проверяем вхождение
                if isinstance(expected_status, list):
                    if response_obj.status_code not in expected_status:
                        error_message = f"Запрос к {method} {url} вернул статус {response_obj.status_code}, ожидался один из {expected_status}. Ответ: {response_obj.text}"
                        self.logger.error(error_message)
                        pytest.fail(error_message)
                else:
                    # Если expected_status - одиночное значение
                    if response_obj.status_code != expected_status:
                        error_message = f"Запрос к {method} {url} вернул статус {response_obj.status_code}, ожидался {expected_status}. Ответ: {response_obj.text}"
                        self.logger.error(error_message)
                        pytest.fail(error_message)

            return response_obj

        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Ошибка сети при запросе к {method} {url}: {e}")
            pytest.fail(f"Ошибка сети при запросе к {method} {url}: {e}")
        except Exception as e:
            self.logger.exception(f"Исключение при выполнении запроса: {e}")
            raise