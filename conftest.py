"""
Глобальные фикстуры для pytest
"""
import pytest
import requests
import json
import random
import re
import logging
from faker import Faker
from sqlalchemy.orm import Session
from models.base_models import TestUser
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from constants import BASE_URL, BOOKING_ENDPOINT, REGISTER_ENDPOINT
from resources.user_creds import SuperAdminCreds
from entities.user import User
from enums.enums import Roles
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper

faker = Faker()


# ==================== БАЗОВЫЕ ФИКСТУРЫ ====================

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


# ==================== ФИКСТУРЫ ДЛЯ АВТОРИЗАЦИИ ====================

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


# ==================== ФИКСТУРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ====================

@pytest.fixture(scope="function")
def test_user() -> TestUser:
    """Фикстура с данными тестового пользователя"""
    password = DataGenerator.generate_random_password()
    # Дополнительная проверка, что пароль валидный
    pattern = r'^(?=.*[a-zA-Zа-яА-Я])(?=.*\d)[a-zA-Zа-яА-Я\d?@#$%^&*_\-+()\[\]{}><\\/\\|"\'.,:;]{8,20}$'
    if not re.match(pattern, password):
        password = DataGenerator.generate_random_password()  # регенерируем

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=password,
        passwordRepeat=password,
        roles=["USER"]
    )


@pytest.fixture(scope="function")
def registered_user(requester, test_user: TestUser) -> TestUser:
    """
    Фикстура для регистрации пользователя.
    Возвращает объект TestUser с обновленными данными.
    """
    user_data = test_user.model_dump()

    request_data = {
        "email": user_data["email"],
        "fullName": user_data["fullName"],
        "password": user_data["password"],
        "passwordRepeat": user_data["passwordRepeat"],
        "roles": user_data.get("roles", ["USER"])
    }

    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        json=request_data,
        expected_status=201
    )

    response_data = response.json()

    return TestUser(
        id=response_data.get("id"),
        email=response_data.get("email"),
        fullName=response_data.get("fullName"),
        password=test_user.password,
        passwordRepeat=test_user.password,
        roles=response_data.get("roles", ["USER"]),
        verified=response_data.get("verified", False),
        banned=response_data.get("banned", False)
    )


@pytest.fixture(scope="function")
def creation_user_data(test_user: TestUser) -> TestUser:
    """Создает объект TestUser с обновленными полями"""
    return test_user.model_copy(update={
        "verified": True,
        "banned": False
    })


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data: TestUser):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    create_response = super_admin.api.user_api.create_user(creation_user_data)
    created_user_id = create_response.json()['id']
    common_user.id = created_user_id

    common_user.api.auth_api.authenticate(common_user.get_creds_dict())

    return common_user


@pytest.fixture
def common_admin(user_session, super_admin, creation_user_data: TestUser):
    new_session = user_session()

    common_admin = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.ADMIN.value],
        new_session)

    create_response = super_admin.api.user_api.create_user(creation_user_data)
    created_user_id = create_response.json()['id']
    common_admin.id = created_user_id

    common_admin.api.auth_api.authenticate(common_admin.get_creds_dict())

    return common_admin


# ==================== ФИКСТУРЫ ДЛЯ БАЗЫ ДАННЫХ ====================

@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()


@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper


@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)


@pytest.fixture(scope="function")
def created_test_movie(db_helper):
    """
    Фикстура, которая создает тестовый фильм в БД
    и удаляет его после завершения теста
    """
    movie_data = DataGenerator.generate_movie_data()

    assert not db_helper.movie_exists_by_name(movie_data['name']), \
        f"Фильм с названием {movie_data['name']} уже существует в БД"

    movie = db_helper.create_test_movie(movie_data)
    print(f"\nСоздан тестовый фильм: {movie.name} (ID: {movie.id})")

    yield movie

    if db_helper.movie_exists_by_id(movie.id):
        db_helper.delete_movie(movie)
        print(f"Тестовый фильм удален: {movie.name}")


# ==================== ФИКСТУРЫ ДЛЯ МУВИ API ====================

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
        "genreId": DataGenerator.generate_genre_id(),  # <-- ИСПРАВЛЕНО!
        "rating": DataGenerator.generate_rating()
    }
    return movie_data



# ==================== ФИКСТУРЫ ДЛЯ BOOKING API ====================

@pytest.fixture(scope="session")
def base_url():
    """Возвращает базовый URL для API."""
    return "https://restful-booker.herokuapp.com"


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
    """Creates a booking and returns the booking ID."""
    response = auth_session.send_request(
        method="POST",
        endpoint=BOOKING_ENDPOINT,
        json=booking_data,
        expected_status=200
    )

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

    yield booking_id


# ==================== НОВЫЕ ФИКСТУРЫ ДЛЯ UI ТЕСТОВ ====================

@pytest.fixture(scope="function")
def browser_context():
    """
    Фикстура для создания браузера и страницы для UI тестов.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        # Можно управлять режимом через переменную окружения
        import os
        headless = os.getenv("HEADLESS", "False").lower() == "true"

        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page(
            viewport={"width": 1280, "height": 720},
            locale="ru-RU"
        )
        yield page
        browser.close()


@pytest.fixture(scope="function")
def login_page(browser_context):
    """
    Фикстура для страницы логина.
    """
    from models.page_object_models import CinescopLoginPage
    return CinescopLoginPage(browser_context)


@pytest.fixture(scope="function")
def register_page(browser_context):
    """
    Фикстура для страницы регистрации.
    """
    from models.page_object_models import CinescopRegisterPage
    return CinescopRegisterPage(browser_context)


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФИКСТУРЫ ====================

@pytest.fixture
def auth_session(requester):
    """
    Фикстура для авторизованной сессии через CustomRequester.
    """
    requester.auth()
    return requester


@pytest.fixture
def logger():
    """Фикстура для логирования"""
    return logging.getLogger(__name__)


# ==================== ПАРАМЕТРИЗОВАННЫЕ ФИКСТУРЫ ====================

@pytest.fixture(params=["MSK", "SPB", "NSK", "KZN", ""])
def test_location(request):
    """Параметризованная фикстура для тестирования локаций"""
    return request.param


@pytest.fixture(params=[1, 5, 10, 20, 50])
def page_size(request):
    """Параметризованная фикстура для тестирования размера страницы"""
    return request.param