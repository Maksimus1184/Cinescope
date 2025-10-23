from faker import Faker
import pytest
import requests
from constants import REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from api.api_manager import ApiManager
from constants import BASE_URL, HEADERS, BOOKING_ENDPOINT
import json


faker = Faker()

@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        json=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user


@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager():
    """
    Инициализирует ApiManager с общей сессией.
    """
    session = requests.Session()
    manager = ApiManager(session=session)
    return manager


@pytest.fixture(scope="session")
def authorized_api_manager(api_manager):
    """
    Фикстура для создания авторизованной сессии через ApiManager.
    Возвращает настроенный ApiManager с установленным токеном авторизации.
    """
    admin_credentials = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    api_manager.auth_api.authenticate(admin_credentials)
    return api_manager



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
def base_url():
    """Возвращает базовый URL для API."""
    return "https://restful-booker.herokuapp.com"

@pytest.fixture(scope="function")
def create_movie_data():
    """
    Генерация случайных данных для создания фильма.
    """
    movie_data = {
        "name": DataGenerator.generate_movie_title(),
        "imageUrl": DataGenerator.generate_image_url(),
        "price": DataGenerator.generate_price(),
        "description": DataGenerator.generate_description(),
        "location": DataGenerator.generate_location(),
        "published": True,
        "genreId": 1
    }
    return movie_data

