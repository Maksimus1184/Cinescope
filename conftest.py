from faker import Faker
import pytest
import requests
from constants import BASE_URL, HEADERS, AUTH_ENDPOINT, BOOKING_ENDPOINT
from custom_requester.custom_requester import CustomRequester
import json


faker = Faker()


@pytest.fixture(scope="session")
def auth_session(base_url):
    login_data = {"username": "admin", "password": "password123"}
    login_session = requests.Session()
    temp_requester = CustomRequester(login_session, base_url)

    # Вызов send_request должен вернуть Response. Он проверит статус.
    response = temp_requester.send_request(
        method="POST",
        endpoint="/auth",
        json=login_data,
        expected_status=200
    )

    # --- Проверяем, что вернулось ---
    # Теперь response - это ОБЪЕКТ RESPONSE.

    # Пытаемся получить JSON, но если что-то не так, это ошибка логина.
    try:
        token_data = response.json()  # Попытка распарсить JSON
    except json.JSONDecodeError:
        # Если не удалось распарсить JSON, значит, логин не удался.
        pytest.fail(
            f"Не удалось распарсить JSON ответа для логина. Статус: {response.status_code}. Ответ: {response.text}")

    # Здесь, если дошли сюда, то response.json() успешно распарсился
    # token_data - это словарь, который мы ожидаем.
    token = token_data.get("token")
    assert token is not None, "Auth token not found in response"

    authorized_session_obj = requests.Session()
    authorized_requester = CustomRequester(authorized_session_obj, base_url)
    authorized_requester.session.headers.update({"Cookie": f"token={token}"})

    print(f"\nАвторизованная сессия создана с токеном: {token[:10]}...")
    yield authorized_requester
    print("\nАвторизованная сессия завершена.")


@pytest.fixture
def booking_data():
    """Создает случайные данные для бронирования."""
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=100000),
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-04-05",
            "checkout": "2024-04-08"
        },
        "additionalneeds": "Cigars"
    }


@pytest.fixture
def create_booking(auth_session, booking_data):
    """Creates a booking and returns the booking ID. (Deletion removed as API does not support DELETE)."""

    # auth_session - это настроенный CustomRequester, который теперь ВСЕГДА возвращает Response объект,
    # если не вызвал pytest.fail.
    response = auth_session.send_request(
        method="POST",
        endpoint=BOOKING_ENDPOINT,
        json=booking_data,
        expected_status=200  # Передаем ожидаемый статус. send_request проверит его.
    )

    # --- Проверки после получения Response объекта ---
    expected_creation_status = 200
    if response.status_code != expected_creation_status:
        pytest.fail(f"Не удалось создать бронирование: Статус {response.status_code}. Ответ: {response.text}")

    try:
        if response.content and len(response.content) > 0:
            booking_info = response.json()
        else:
            pytest.fail(f"Получен ответ с статус-кодом {response.status_code}, но тело ответа пустое.")
    except json.JSONDecodeError:
        pytest.fail(f"Не удалось распарсить JSON из ответа создания бронирования. Ответ: {response.text}")

    booking_id = booking_info.get("bookingid")
    assert booking_id is not None, f"Не удалось получить bookingid из ответа создания бронирования. Ответ: {booking_info}"

    print(f"Бронирование успешно создано с ID: {booking_id}.")

    # Yield: возвращаем booking_id для теста.
    yield booking_id
@pytest.fixture(scope="session")
def requester():
    """Фикстура для создания экземпляра CustomRequester."""
    session = requests.Session()
    # Устанавливаем общие заголовки для сессии, если они есть
    session.headers.update(HEADERS)
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def base_url():
    """Возвращает базовый URL для API."""
    return "https://restful-booker.herokuapp.com"