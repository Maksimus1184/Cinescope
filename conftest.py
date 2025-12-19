from faker import Faker
import pytest
import requests
from resources.user_creds import SuperAdminCreds
from entities.user import User
from enums.enums import Roles
from constants import REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from api.api_manager import ApiManager
from constants import BASE_URL, HEADERS, BOOKING_ENDPOINT
from models.base_models import TestUser
import json
import logging



faker = Faker()

@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=['USER']
    )

@pytest.fixture(scope="function")
def registered_user(requester, test_user: TestUser) -> TestUser:
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    Возвращает объект TestUser с заполненным id.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        json=test_user,
        expected_status=201
    )
    response_data = response.json()

    # Получаем словарь из test_user, исключая поле 'id'
    user_dict = test_user.model_dump(exclude={'id'})
    # Создаем новый объект TestUser с id из ответа
    registered_user = TestUser(**user_dict, id=response_data["id"])
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

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    response = super_admin.api.auth_api.send_request(
        method="POST",
        endpoint="/login",
        json=super_admin.get_creds_dict(),
        expected_status=[200, 201]
    )

    response_data = response.json()
    token = response_data["accessToken"]
    super_admin.api.session.headers.update({"Authorization": f"Bearer {token}"})

    return super_admin


@pytest.fixture(scope="function")
def creation_user_data(test_user: TestUser) -> TestUser:
    """Создает объект TestUser с обновленными полями"""
    # Просто копируем объект и обновляем нужные поля
    return test_user.model_copy(update={
        "verified": True,
        "banned": False
    })


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data: TestUser):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,  # Атрибут объекта TestUser
        creation_user_data.password,
        [Roles.USER.value],  # Явно задаем список с ролью USER
        new_session)

    # Создаем пользователя через super_admin
    create_response = super_admin.api.user_api.create_user(creation_user_data)

    # Получаем ID созданного пользователя
    created_user_id = create_response.json()['id']

    # Сохраняем ID в объекте common_user
    common_user.id = created_user_id

    # Аутентифицируем созданного пользователя
    common_user.api.auth_api.authenticate(common_user.get_creds_dict())

    return common_user


@pytest.fixture
def common_admin(user_session, super_admin, creation_user_data: TestUser):
    new_session = user_session()

    common_admin = User(
        creation_user_data.email,  # Атрибут объекта
        creation_user_data.password,
        [Roles.ADMIN.value],  # Явно задаем список с ролью ADMIN
        new_session)

    # Создаем пользователя через super_admin
    create_response = super_admin.api.user_api.create_user(creation_user_data)

    # Получаем ID созданного пользователя
    created_user_id = create_response.json()['id']

    # Сохраняем ID в объекте common_admin
    common_admin.id = created_user_id

    # Аутентифицируем созданного пользователя
    common_admin.api.auth_api.authenticate(common_admin.get_creds_dict())

    return common_admin