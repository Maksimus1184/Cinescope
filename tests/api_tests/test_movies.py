import random
import string

class TestMoviesAPI:

    def test_create_movie_as_admin(self, admin_movies_api_client, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа.
        """
        # Используем предварительно авторизованный клиент
        response = admin_movies_api_client.create_movie(create_movie_data)

        assert response.status_code == 201, f"Ожидаемый статус 201, но {response.status_code}. ответ: {response.text}"
        print(f"Код ответа: {response.status_code}, текст ответа: {response.text}")
        response_data = response.json()

        assert response_data["name"] == create_movie_data["name"]
        assert response_data["imageUrl"] == create_movie_data["imageUrl"]
        assert response_data["price"] == create_movie_data["price"]
        assert response_data["description"] == create_movie_data["description"]
        assert response_data["location"] == create_movie_data["location"]
        # Проверка булевого значения
        assert response_data["published"] == create_movie_data["published"]
        assert response_data["genreId"] == create_movie_data["genreId"]
        # Дополнительно, если API возвращает ID созданного фильма
        assert "id" in response_data, "ID фильма отсутствует в ответе"

    def test_get_movies(self, admin_movies_api_client):
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

        response = admin_movies_api_client.get_movies(params=params)
        assert response.status_code == 200, f"Ошибка: код {response.status_code}, Текст ошибки: {response.text}"
        response_data = response.json()

        assert "movies" in response_data, "В ответе отсутствует 'movies'."
        assert isinstance(response_data["movies"], list), "'movies' должен быть списком."

        # Проверяем количество фильмов на соответствие pageSize
        if response_data["movies"]:
             assert len(response_data["movies"]) <= params["pageSize"]

        # Проверим другие параметры
        for movie in response_data["movies"]:
            assert movie["location"] in params["locations"]
            assert movie["published"] == params["published"]

        print(f"Код ответа {response.status_code}, Текст ответа: {response.text}")

    def test_create_and_get_movie_id_as_admin(self, admin_movies_api_client, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа и его поиск по ID.
        """
        # Сначала создаем фильм
        response = admin_movies_api_client.create_movie(create_movie_data)
        assert response.status_code == 201, f"Ошибка при создании фильма: код {response.status_code}, Текст ошибки: {response.text}"

        created_movie = response.json()
        movie_id = created_movie["id"]
        print(f"Фильм создан с ID: {movie_id}")

        # Теперь получаем фильм по ID
        get_response = admin_movies_api_client.get_movie_by_id(movie_id)
        assert get_response.status_code == 200, f"Ошибка при получении фильма по ID: код {get_response.status_code}, Текст ошибки: {get_response.text}"

        movie_data_by_id = get_response.json()

        # Проверяем данные полученного фильма
        assert movie_data_by_id["id"] == movie_id
        assert movie_data_by_id["name"] == create_movie_data["name"]
        assert movie_data_by_id["price"] == create_movie_data["price"]
        assert movie_data_by_id["description"] == create_movie_data["description"]
        assert movie_data_by_id["imageUrl"] == create_movie_data["imageUrl"]
        assert movie_data_by_id["location"] == create_movie_data["location"]
        assert movie_data_by_id["published"] == create_movie_data["published"]
        assert movie_data_by_id["genreId"] == create_movie_data["genreId"]
        assert "createdAt" in movie_data_by_id
        assert "reviews" in movie_data_by_id
        assert "genre" in movie_data_by_id
        assert "name" in movie_data_by_id["genre"]

        print(f"✅ Фильм успешно создан и получен по ID {movie_id}")
        print(f"Название: {movie_data_by_id['name']}")
        print(f"Жанр: {movie_data_by_id['genre']['name']}")
        print(f"Статус публикации: {movie_data_by_id['published']}")

    def test_update_movie_as_admin(self, admin_movies_api_client, create_movie_data):
        """
        Тест на редактирование фильма с использованием токена админа.
        """
        # Сначала создаем фильм
        create_response = admin_movies_api_client.create_movie(create_movie_data)
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        print(f"Фильм создан с ID: {movie_id}")

        # Генерируем уникальные данные
        random_suffix = ''.join(random.choices(string.ascii_letters, k=8))
        update_data = {
            "name": f"Movie_{random_suffix}",
            "price": random.randint(100, 1000),
        }

        # Редактируем фильм
        update_response = admin_movies_api_client.update_movie(movie_id, update_data)
        assert update_response.status_code == 200

        updated_movie = update_response.json()
        assert updated_movie["name"] == update_data["name"]
        assert updated_movie["price"] == update_data["price"]

        print(f"✅ Фильм с ID {movie_id} успешно отредактирован")

    def test_delete_movie(self, admin_movies_api_client, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа и его поиск по ID.
        """
        # Сначала создаем фильм
        response = admin_movies_api_client.create_movie(create_movie_data)
        assert response.status_code == 201, f"Ошибка при создании фильма: код {response.status_code}, Текст ошибки: {response.text}"

        created_movie = response.json()
        movie_id = created_movie["id"]
        print(f"Фильм создан с ID: {movie_id}")

        # Теперь получаем фильм по ID
        get_response = admin_movies_api_client.delete_movie(movie_id)
        assert get_response.status_code == 200, f"Ошибка при получении фильма по ID: код {get_response.status_code}, Текст ошибки: {get_response.text}"
        print(f"Фильм с ID: {movie_id} удален")
        # Теперь пробуем получить удаленный фильм по ID
        get_response = admin_movies_api_client.get_movie_by_id(movie_id, expected_status=404)
        print(" Фильм успешно удален и больше не доступен")

    def test_create_unpublished_movie_with_invalid_location(self, admin_movies_api_client, create_movie_data):
        """
        Негативный тест: создание неопубликованного фильма с невалидной локацией.
        Ожидается ошибка 400.
        """
        # Модифицируем данные: неопубликованный фильм + невалидная локация
        invalid_movie_data = create_movie_data.copy()
        invalid_movie_data["published"] = False
        invalid_movie_data["location"] = "BKK"  # Не MSK или SPB

        # Пытаемся создать фильм с невалидными данными
        response = admin_movies_api_client.create_movie(invalid_movie_data,expected_status=400)

        assert response.status_code == 400, f"Ожидался статус 400, но получен {response.status_code}. Ответ: {response.text}"

        response_data = response.json()

        # Проверяем, что в ответе есть информация об ошибке
        assert "message" in response_data or "error" in response_data, "В ответе отсутствует сообщение об ошибке"
        print(f"Тест пройден: получена ожидаемая ошибка - {response_data}")

    def test_create_movie_with_invalid_value(self, admin_movies_api_client, create_movie_data):
        """
        Тест на создание фильма с использованием токена админа.
        """
        # Используем предварительно авторизованный клиент
        response = admin_movies_api_client.create_movie(create_movie_data)

        assert response.status_code == 201, f"Ожидаемый статус 201, но {response.status_code}. ответ: {response.text}"
        print(f"Код ответа: {response.status_code}, текст ответа: {response.text}")
        response_data = response.json()

        assert response_data["name"] == create_movie_data["name"]
        assert response_data["imageUrl"] == create_movie_data["imageUrl"]
        assert response_data["price"] == create_movie_data["price"]
        assert response_data["description"] == create_movie_data["description"]
        assert response_data["location"] == create_movie_data["location"]
        # Проверка булевого значения
        assert response_data["published"] == create_movie_data["published"]
        assert response_data["genreId"] == create_movie_data["genreId"]
        # Дополнительно, если API возвращает ID созданного фильма
        assert "id" in response_data, "ID фильма отсутствует в ответе"

    def test_get_movies_without_params(self, admin_movies_api_client):
        """
        Негативный тест: получение списка фильмов без обязательных параметров.
        """
        # Тест без параметров
        no_params= {
        }
        response = admin_movies_api_client.get_movies(params=no_params)
        assert response.status_code == 200, f"Ожидалась ошибка 400 без параметров, но получен {response.status_code}"
        print(f"Без pageSize: код {response.status_code}, ответ: {response.text}")

    def test_get_movie_by_nonexistent_id(self, admin_movies_api_client):
        """
        Негативный тест: поиск фильма по несуществующему ID.
        """
        # Используем заведомо несуществующий ID
        nonexistent_id = 999999999

        # Пытаемся получить фильм по несуществующему ID, ожидаем 404
        get_response = admin_movies_api_client.get_movie_by_id(movie_id=nonexistent_id,expected_status=404)

        # Проверяем, что в ответе есть информация об ошибке
        response_data = get_response.json()
        assert "message" in response_data, "В ответе отсутствует сообщение об ошибке"
        assert response_data["message"] == "Фильм не найден"

        print(f"Тест пройден: для несуществующего ID {nonexistent_id} получена ожидаемая ошибка 404")
        print(f"Сообщение об ошибке: {response_data}")

    def test_update_movie_with_empty_data(self, admin_movies_api_client, create_movie_data):
        """
        Тест: обновление фильма с пустыми данными.
        """
        # Сначала создаем фильм
        create_response = admin_movies_api_client.create_movie(create_movie_data)
        assert create_response.status_code == 201
        created_movie = create_response.json()
        movie_id = created_movie["id"]
        print(f"Фильм создан с ID: {movie_id}")

        # Пытаемся обновить фильм с пустыми данными - ожидаем успех
        empty_data = {}
        response = admin_movies_api_client.update_movie(
            movie_id=movie_id,
            update_data=empty_data,
            expected_status=200  # Ожидаем успех, так как пустое тело допустимо
        )

        assert response.status_code == 200
        print(f"Пустые данные: код {response.status_code} - фильм не изменился")

        # Проверяем, что данные фильма остались прежними
        updated_movie = response.json()
        assert updated_movie["name"] == created_movie["name"]
        assert updated_movie["price"] == created_movie["price"]

    def test_update_movie_with_invalid_id(self, admin_movies_api_client, create_movie_data):
        """
        Негативный тест: обновление несуществующего фильма.
        """
        invalid_movie_id = 999999999

        response = admin_movies_api_client.update_movie(
            movie_id=invalid_movie_id,
            update_data={"name": "New Name"},
            expected_status=404
        )

        assert response.status_code == 404
        response_data = response.json()
        assert "message" in response_data
        print(f"Несуществующий ID: код {response.status_code}, ошибка: {response_data['message']}")

    def test_update_movie_with_invalid_data(self, admin_movies_api_client, create_movie_data):
        """
        Негативный тест: обновление фильма с невалидными типами данных.
        """
        # Сначала создаем фильм
        create_response = admin_movies_api_client.create_movie(create_movie_data)
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]

        # Пытаемся обновить с невалидными данными
        invalid_data = {
            "price": "invalid_price",  # Строка вместо числа
            "published": "not_a_boolean",  # Строка вместо boolean
        }

        response = admin_movies_api_client.update_movie(
            movie_id=movie_id,
            update_data=invalid_data,
            expected_status=400
        )

        assert response.status_code == 400
        print(f"Невалидные типы: код {response.status_code}, ответ: {response.text}")

    def test_delete_movie_with_invalid_id(self, admin_movies_api_client, create_movie_data):
        """
        Негативный тест: обновление несуществующего фильма.
        """
        invalid_movie_id = 88888888888

        response = admin_movies_api_client.delete_movie(
            movie_id=invalid_movie_id,
            expected_status=404
        )

        assert response.status_code == 404
        response_data = response.json()
        assert "message" in response_data
        print(f"Несуществующий ID: код {response.status_code}, ошибка: {response_data['message']}")