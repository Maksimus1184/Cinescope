import requests
import pytest
from constants import HEADERS, BASE_URL, BOOKING_ENDPOINT

class TestBookings:
    def test_create_booking(self, auth_session, booking_data, create_booking):
        assert "Cookie" in auth_session.session.headers, "Заголовок 'Cookie' с токеном авторизации отсутствует в сессии."
        assert "token=" in auth_session.session.headers["Cookie"], "Токен авторизации не найден в заголовке 'Cookie'."
        print(f"Заголовок авторизации 'Cookie' найден в сессии: {auth_session.session.headers['Cookie'][:20]}...")
        # Проверяем, что бронирование можно получить по ID
        booking_id = create_booking
        get_response = auth_session.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=200
        )

        # Теперь проверяем ответ GET-запроса
        assert get_response.status_code == 200, f"Не удалось получить бронирование {booking_id} после создания. Статус: {get_response.status_code}. Ответ: {get_response.text}"


        print(f"Бронирование с ID {booking_id} успешно получено и проверено.")

        # Удаляем бронирование
        delete_response = auth_session.send_request(
            method="DELETE",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=201
        )

        # Проверяем, что удаление прошло успешно (согласно ожидаемому статусу)
        assert delete_response.status_code == 201, f"Ошибка удаления бронирования {booking_id}. Статус: {delete_response.status_code}. Ответ: {delete_response.text}"
        print(f"Бронирование с ID {booking_id} успешно удалено.")

        # Проверяем, что бронирование больше недоступно
        get_response_after_delete = auth_session.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=404
        )

        # Проверяем, что GET-запрос к удаленному ресурсу вернул 404
        assert get_response_after_delete.status_code == 404, f"Бронирование {booking_id} все еще доступно после удаления. Статус: {get_response_after_delete.status_code}. Ответ: {get_response_after_delete.text}"
        print(f"Подтверждено, что бронирование с ID {booking_id} более недоступно.")

    def test_full_change_booking(self, auth_session, booking_data, create_booking):
        """Тест на полное обновление бронирования."""

        booking_id = create_booking
        print(f"Тестируем обновление бронирования с ID: {booking_id}.")

        # Получаем данные созданного бронирования (чтобы сравнить с исходными)
        get_initial_response = auth_session.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=200
        )
        assert get_initial_response.status_code == 200, f"Не удалось получить бронирование {booking_id} после создания. Статус: {get_initial_response.status_code}. Ответ: {get_initial_response.text}"

        initial_booking_data_from_api = get_initial_response.json()

        # Теперь сравниваем данные из booking_details_from_api с booking_data, переданным в фикстуру
        assert initial_booking_data_from_api.get("firstname") == booking_data["firstname"], \
            f"Исходное имя ({initial_booking_data_from_api.get('firstname')}) не совпадает с ожидаемым ({booking_data['firstname']})"
        assert initial_booking_data_from_api.get("totalprice") == booking_data["totalprice"], \
            f"Исходная цена ({initial_booking_data_from_api.get('totalprice')}) не совпадает с ожидаемой ({booking_data['totalprice']})"

        print("Исходные данные созданного бронирования совпадают.")

        # Обновляем данные бронирования
        update_data = {
            "firstname": "Jim",
            "lastname": "Brown",
            "totalprice": 111,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-04",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # PUT запрос на обновление данных бронирования
        update_response = auth_session.send_request(
            method="PUT",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            json=update_data,
            expected_status=200
        )
        assert update_response.status_code == 200, f"Ошибка обновления бронирования {booking_id}. Статус: {update_response.status_code}. Ответ: {update_response.text}"
        print(f"Бронирование с ID {booking_id} успешно обновлено.")

        # Получаем обновленные данные бронирования и проверяем
        # Снова делаем GET-запрос, чтобы получить обновленные данные
        get_updated_response = auth_session.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=200
        )
        assert get_updated_response.status_code == 200, f"Не удалось получить обновленное бронирование {booking_id}. Статус: {get_updated_response.status_code}. Ответ: {get_updated_response.text}"

        updated_booking_data = get_updated_response.json()

        # Проверяем, что данные обновились правильно
        # Сравниваем данные из update_data с данными, полученными после PUT
        # Используем .get() для безопасного доступа к полям
        # Проверяем, что поле firstname обновилось
        assert updated_booking_data.get("firstname") == "Jim", \
            f"Ожидалось имя Jim, но получено '{updated_booking_data.get('firstname')}'"

        # Добавьте проверки для других полей, которые вы обновили
        assert updated_booking_data.get("lastname") == "Brown", \
            f"Ожидалась фамилия Brown, но получена '{updated_booking_data.get('lastname')}'"
        assert updated_booking_data.get("totalprice") == 111, \
            f"Ожидалась цена 111, но получена '{updated_booking_data.get('totalprice')}'"

        print(f"Все данные обновленного бронирования (ID {booking_id}) успешно проверены.")


    def test_partial_booking_update(self, auth_session, booking_data, create_booking):
            """Тест на частичное обновление бронирования"""
            booking_id = create_booking
            # передаем данные для изменения
            partial_update_data = {
                "firstname": "Лариса",
                "additionalneeds": "Ужин"
            }

            # PATCH запрос
            patch_booking_response = auth_session.send_request(
                method="PATCH",
                endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
                json=partial_update_data,
                expected_status=200
            )

            assert patch_booking_response.status_code == 200, f"Ошибка: {patch_booking_response.status_code}, {patch_booking_response.text}"
            print(f"Данные бронирования (ID {booking_id}) частично изменены.")
            # Получаем бронирование
            get_booking_response = auth_session.send_request(
                method="GET",
                endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
                expected_status=200
            )

            assert get_booking_response.status_code == 200, f"Ошибка: {get_booking_response.status_code}, {get_booking_response.text}"
            partial_updated_booking_data = get_booking_response.json()
            print(f"Успешно получены данные бронирования (ID {booking_id}) с  частичными изменениями.")
            # Проверяем изменение данных
            assert partial_updated_booking_data['firstname'] == "Лариса", f"Ожидалось имя Лариса, но имя {partial_updated_booking_data['firstname']}"
            assert partial_updated_booking_data['additionalneeds'] == "Ужин", f"Ожидалось дополнительно Ужин, но дополнительно {partial_updated_booking_data['additionalneeds']}"
            print(f"Новые данные бронирования (ID {booking_id}) успешно применены.")
            # Проверяем, что другие данные из первоначального бронирования не изменились
            assert partial_updated_booking_data['lastname'] == booking_data['lastname'], f"Ожидалась фамилия 'Brown', но фамилия {partial_updated_booking_data['lastname']}"
            assert partial_updated_booking_data['totalprice'] == booking_data['totalprice'], f"Ожидалась цена 111, но цена {partial_updated_booking_data['totalprice']}"
            print(f"Ранее внесенные данные бронирования (ID {booking_id}) не изменены.")

    def test_negativ_booking(self, auth_session, booking_data):
        """
        Тест на проверку некорректного создания бронирования при пропуске обязательного поля 'totalprice'.
        Ожидается ответ 500 Bad Request.
        """

        booking_payload_missing_price = {
            "firstname": "Лариса",
            "lastname": "Brown",
            # "totalprice" отсутствует
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-04",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # Определяем ожидаемый статус-код.
        expected_error_status = 500

        # POST запрос на создание бронирования с неполными данными
        response = auth_session.send_request(
            method="POST",
            endpoint=BOOKING_ENDPOINT,
            json=booking_payload_missing_price,
            expected_status=expected_error_status
        )

        print(f"Тест успешно пройден: API вернул ожидаемую ошибку {response.status_code}.")

    def test_negativ_value_booking_1(self, auth_session, booking_data):
        """Тест на проверку кода 400 при неверном формате данных"""

        data = {
            "firstname": "11232251561541",
            "lastname": "325164646147+6768+817+8778",
            "totalprice": "asjsdh)(*;:?:%;:?*(",  # totalprice передан текстом
            "depositpaid": True,
            "bookingdates": {
                "checkin": "рлсапрсрмпрсарпмпрср",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # Определяем ожидаемый статус-код.
        expected_error_status = 200

        # POST запрос на создание бронирования с неверными данными
        response = auth_session.send_request(
            method="POST",
            endpoint=BOOKING_ENDPOINT,
            json=data,
            expected_status=expected_error_status
        )

        assert response.status_code == 200, f"Ожидался статус-код 200, но {response.status_code},{response.text}"
        print(f"Тест успешно пройден: API вернул ожидаемую ошибку {response.status_code}.")


    def test_update_nonexistent_booking(self, auth_session):
        """Тест на попытку обновления несуществующего booking_id"""
        booking_id = 10000000

        data = {
            "firstname": "Надежда",
            "lastname": "Иванова",
            "totalprice": 150,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2024-12-15",
                "checkout": "2024-12-20"
            },
            "additionalneeds": "Breakfast 14-058"
        }

        # POST запрос на полное обновление несуществующего booking_id
        put_response = auth_session.send_request(
            method="POST",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            json=data
        )
        assert put_response.status_code == 404, f"Ожидалась ошибка 404, но ошибка {put_response.status_code}, {put_response.text}"
        print(f"Тест успешно пройден: API вернул ожидаемую ошибку {put_response.status_code}, {put_response.text}.")
        patch_data = {"firstname": "PartiallyUpdatedName"}  # Partial update data
        # Try PATCH request
        patch_response = auth_session.send_request(
            method="POST",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            json=patch_data
        )

        assert patch_response.status_code == 404, f"Ожидалась ошибка 200, но ошибка {patch_response.status_code}, {patch_response.text}"
        print(f"Тест успешно пройден: API вернул ожидаемую ошибку {patch_response.status_code}, {patch_response.text}.")

    def test_negativ_value_booking(self, auth_session, booking_data):
        """Тест на проверку кода 500 при передаче пустых данных"""

        data = {}

        # POST запрос на создание бронирования
        post_response = auth_session.send_request(
            method="POST",
            endpoint= BOOKING_ENDPOINT,
            json=data
        )

        # Проверяем статус-код 400 (Bad Request)
        assert post_response.status_code == 500, f"Ожидался статус-код 400, но {post_response.status_code},{post_response.text}"
        print(f"Тест успешно пройден: API вернул ожидаемую ошибку {post_response.status_code}, {post_response.text}.")






