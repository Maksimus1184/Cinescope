import pytest
import allure
from datetime import datetime


# ==================== PYDANTIC MODELS ====================
from pydantic import BaseModel, validator
from typing import List, Optional


class Genre(BaseModel):
    """Модель жанра"""
    id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class Review(BaseModel):
    """Модель отзыва"""
    id: int
    movieId: int
    userId: int
    rating: int
    comment: str
    createdAt: datetime

    class Config:
        from_attributes = True


class MovieResponse(BaseModel):
    """Модель ответа для одного фильма"""
    id: int
    name: str
    imageUrl: Optional[str] = None
    price: int
    description: str
    location: str
    published: bool
    genreId: int
    createdAt: datetime
    reviews: List[Review] = []
    genre: Optional[Genre] = None

    @validator('price')
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('price must be positive')
        return v

    @validator('location')
    def location_must_be_valid(cls, v):
        if v not in ['MSK', 'SPB']:
            raise ValueError('location must be MSK or SPB')
        return v

    class Config:
        from_attributes = True


class MoviesListResponse(BaseModel):
    """Модель ответа для списка фильмов"""
    movies: List[MovieResponse]
    total: Optional[int] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== ТЕСТЫ ====================

@allure.epic("Movies API")
@allure.feature("CRUD Operations")
class TestMoviesAPI:
    """Тесты CRUD операций с фильмами"""

    @allure.story("Create Movie")
    @allure.title("Создание фильма администратором")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_create_movie_as_admin(self, authorized_api_manager, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа.
        """
        with allure.step("Создание фильма через API"):
            response = authorized_api_manager.movies_api.create_movie(create_movie_data)
            response_data = response.json()
            allure.attach(response.text, name="Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка данных ответа"):
            assert response_data["name"] == create_movie_data["name"]
            assert response_data["imageUrl"] == create_movie_data["imageUrl"]
            assert response_data["price"] == create_movie_data["price"]
            assert response_data["description"] == create_movie_data["description"]
            assert response_data["location"] == create_movie_data["location"]
            assert response_data["published"] == create_movie_data["published"]
            assert response_data["genreId"] == create_movie_data["genreId"]
            assert "id" in response_data, "ID фильма отсутствует в ответе"

        with allure.step("Проверка схемы ответа через Pydantic модель"):
            movie = MovieResponse.model_validate(response_data)
            assert movie.id > 0
            assert movie.price > 0

        allure.attach(
            f"Создан фильм с ID: {response_data['id']}",
            name="Created movie ID",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("Get Movies")
    @allure.title("Получение списка фильмов с фильтрацией")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_get_movies(self, authorized_api_manager):
        """
        Тест на получение списка фильмов.
        """
        params = {
            "pageSize": 10,
            "page": 1,
            "minPrice": 1,
            "maxPrice": 1000,
            "locations": ["MSK", "SPB"],
            "published": True,
            "createdAt": "asc"
        }

        with allure.step(f"Получение списка фильмов с параметрами: {params}"):
            response = authorized_api_manager.movies_api.get_movies(params=params)
            response_data = response.json()
            allure.attach(response.text, name="Response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка структуры ответа"):
            assert "movies" in response_data, "В ответе отсутствует 'movies'."
            assert isinstance(response_data["movies"], list), "'movies' должен быть списком."

        with allure.step("Проверка схемы ответа через Pydantic модель"):
            movies_list = MoviesListResponse.model_validate(response_data)
            assert len(movies_list.movies) <= params["pageSize"]

        with allure.step("Проверка данных фильмов"):
            for movie in response_data["movies"]:
                assert movie["location"] in params["locations"]
                assert movie["published"] == params["published"]

        allure.attach(
            f"Код ответа {response.status_code}\nНайдено фильмов: {len(response_data['movies'])}",
            name="Response details",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("Create and Get Movie")
    @allure.title("Создание фильма и получение по ID")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_create_and_get_movie_id_as_admin(self, authorized_api_manager, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа и его поиск по ID.
        """
        with allure.step("Создание фильма через API"):
            response = authorized_api_manager.movies_api.create_movie(create_movie_data)
            created_movie = response.json()
            movie_id = created_movie["id"]
            allure.attach(str(movie_id), name="Created movie ID", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"Получение фильма по ID: {movie_id}"):
            get_response = authorized_api_manager.movies_api.get_movie_by_id(movie_id)
            movie_data_by_id = get_response.json()

        with allure.step("Проверка данных полученного фильма"):
            assert movie_data_by_id["id"] == movie_id
            assert movie_data_by_id["name"] == create_movie_data["name"]
            assert movie_data_by_id["price"] == create_movie_data["price"]
            assert movie_data_by_id["description"] == create_movie_data["description"]
            assert movie_data_by_id["imageUrl"] == create_movie_data["imageUrl"]
            assert movie_data_by_id["location"] == create_movie_data["location"]
            assert movie_data_by_id["published"] == create_movie_data["published"]
            assert movie_data_by_id["genreId"] == create_movie_data["genreId"]

        with allure.step("Проверка схемы через Pydantic модель"):
            movie = MovieResponse.model_validate(movie_data_by_id)
            assert "createdAt" in movie_data_by_id
            assert "reviews" in movie_data_by_id
            assert "genre" in movie_data_by_id

    @allure.story("Update Movie")
    @allure.title("Редактирование фильма администратором")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_update_movie_as_admin(self, authorized_api_manager, create_movie_data):
        """
        Тест на редактирование фильма с использованием токена админа.
        """
        import random
        import string

        with allure.step("Создание фильма"):
            create_response = authorized_api_manager.movies_api.create_movie(create_movie_data)
            assert create_response.status_code == 201
            movie_id = create_response.json()["id"]
            allure.attach(str(movie_id), name="Created movie ID", attachment_type=allure.attachment_type.TEXT)

        random_suffix = ''.join(random.choices(string.ascii_letters, k=8))
        update_data = {
            "name": f"Movie_{random_suffix}",
            "price": random.randint(100, 1000),
        }

        with allure.step(f"Обновление фильма данными: {update_data}"):
            update_response = authorized_api_manager.movies_api.update_movie(movie_id, update_data)
            updated_movie = update_response.json()

        with allure.step("Проверка обновленных данных"):
            assert updated_movie["name"] == update_data["name"]
            assert updated_movie["price"] == update_data["price"]

        with allure.step("Проверка через GET запрос"):
            get_response = authorized_api_manager.movies_api.get_movie_by_id(movie_id)
            assert get_response.status_code == 200
            movie_from_get = get_response.json()
            assert movie_from_get["name"] == update_data["name"]
            assert movie_from_get["price"] == update_data["price"]

    @allure.story("Delete Movie")
    @allure.title("Удаление фильма администратором")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_delete_movie(self, authorized_api_manager, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа и его удаление.
        """
        with allure.step("Создание фильма"):
            response = authorized_api_manager.movies_api.create_movie(create_movie_data)
            created_movie = response.json()
            movie_id = created_movie["id"]
            allure.attach(str(movie_id), name="Created movie ID", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"Удаление фильма с ID: {movie_id}"):
            delete_response = authorized_api_manager.movies_api.delete_movie(movie_id)
            assert delete_response.status_code == 200

        with allure.step("Проверка, что фильм недоступен через API"):
            get_response = authorized_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)
            assert get_response.status_code == 404


@allure.epic("Movies API")
@allure.feature("API + DB Integration")
class TestMovieAPIWithDB:
    """
    Тест для проверки создания и удаления фильма через API
    с проверкой состояния базы данных
    """

    @allure.story("Create and Delete with DB Check")
    @allure.title("Создание и удаление фильма с проверкой БД")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_and_delete_movie_api_db_check(self, authorized_api_manager, db_helper):
        """
        Тест проверяет:
        1. До начала тестирования в базе отсутствует фильм
        2. После вызова запроса на создание в базе появился фильм
        3. После удаления фильма через API в базе также удаляется данный объект
        """
        from utils.data_generator import DataGenerator

        with allure.step("Генерация данных для фильма"):
            movie_data = DataGenerator.generate_movie_data()
            movie_name = movie_data['name']

        with allure.step("Создание копии данных для API"):
            api_movie_data = movie_data.copy()
            api_movie_data.pop('id', None)

            # Исправление формата createdAt для API
            if 'createdAt' in api_movie_data and not api_movie_data['createdAt'].endswith('Z'):
                api_movie_data['createdAt'] = api_movie_data['createdAt'] + 'Z'

            allure.attach(str(api_movie_data), name="API Request Data", attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка, что фильма нет в БД до теста"):
            assert not db_helper.movie_exists_by_name(movie_name), \
                f"Фильм '{movie_name}' уже существует в БД до начала теста"

        with allure.step("Создание фильма через API"):
            response = authorized_api_manager.movies_api.create_movie(
                movie_data=api_movie_data,
                expected_status=201
            )
            created_movie_id = response.json().get('id')
            assert created_movie_id is not None, "В ответе API отсутствует ID созданного фильма"
            allure.attach(str(created_movie_id), name="Created movie ID", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Проверка, что фильм появился в БД"):
            assert db_helper.movie_exists_by_id(created_movie_id), \
                f"Фильм с ID {created_movie_id} не найден в БД"

            db_movie = db_helper.get_movie_by_id(created_movie_id)
            assert db_movie.name == movie_name, "Название фильма не совпадает"
            assert db_movie.price == api_movie_data['price'], "Цена фильма не совпадает"
            assert db_movie.location == api_movie_data['location'], "Локация не совпадает"
            assert db_movie.genre_id == api_movie_data['genreId'], "ID жанра не совпадает"

            allure.attach(
                f"Фильм найден в БД: {db_movie.name}, ID: {db_movie.id}",
                name="DB Check",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Удаление фильма через API"):
            delete_response = authorized_api_manager.movies_api.delete_movie(
                movie_id=created_movie_id,
                expected_status=[200, 204]
            )
            allure.attach(
                f"Статус удаления: {delete_response.status_code}",
                name="Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка, что фильм удален из БД"):
            assert not db_helper.movie_exists_by_id(created_movie_id), \
                f"Фильм с ID {created_movie_id} все еще существует в БД"
            assert not db_helper.movie_exists_by_name(movie_name), \
                f"Фильм с названием '{movie_name}' все еще существует в БД"

            allure.attach("Фильм успешно удален из БД", name="Cleanup", attachment_type=allure.attachment_type.TEXT)