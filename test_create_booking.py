import requests
import pytest
from constants import HEADERS, BASE_URL
from faker import Faker

class TestBookings:
    def test_create_booking(self, auth_session, booking_data):
        # Создаём бронирование
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking.status_code == 200, "Ошибка при создании брони"

        booking_id = create_booking.json().get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert create_booking.json()["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert create_booking.json()["booking"]["totalprice"] == booking_data["totalprice"], "Заданная стоимость не совпадает"

        # Проверяем, что бронирование можно получить по ID
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Удаляем бронирование
        deleted_booking = auth_session.delete(f"{BASE_URL}/booking/{booking_id}")
        assert deleted_booking.status_code == 201, "Бронь не удалилась"

        # Проверяем, что бронирование больше недоступно
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 404, "Бронь не удалилась"

    def test_full_change_booking(self, auth_session, booking_data):
        """Тест на полное обновление бронирования"""

        # Создаем бронирование
        create_booking_response = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking_response.status_code == 200, f"Error creating booking: {create_booking_response.status_code}, {create_booking_response.text}"

        create_booking_data = create_booking_response.json()
        booking_id = create_booking_data['bookingid']
        assert booking_id is not None, "Booking ID not found in the response"

        # Проверяем firstname, totalprice
        assert create_booking_data["booking"]["firstname"] == booking_data["firstname"], "Created firstname does not match"
        assert create_booking_data["booking"]["totalprice"] == booking_data["totalprice"], "Created totalprice does not match"

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
        update_url = f"{BASE_URL}/booking/{booking_id}"
        update_booking_response = auth_session.put(update_url, json=update_data)
        assert update_booking_response.status_code == 200, f"Ошибка: {update_booking_response.status_code}, {update_booking_response.text}"

        updated_booking_data = update_booking_response.json()

        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"

        # Проверяем все данные бронирования
        assert updated_booking_data['firstname'] == 'Jim', f"Ожидалось имя 'Jim', но имя '{updated_booking_data['firstname']}'"
        assert updated_booking_data['lastname'] == 'Brown', f"Ожидалась фамилия 'Brown', но фамилия '{updated_booking_data['lastname']}'"
        assert updated_booking_data['totalprice'] == 111, f"Ожидалась цена 111, но цена '{updated_booking_data['totalprice']}'"
        assert updated_booking_data['depositpaid'] == True, f"Ожидался депозит True, но депозит '{updated_booking_data['depositpaid']}'"
        assert updated_booking_data["bookingdates"]["checkin"]== "2025-01-04", f"Ожидалась дата заезда 2025-01-04, но дата заезда '{updated_booking_data["bookingdates"]["checkin"]}'"
        assert updated_booking_data["bookingdates"]["checkout"] == "2025-01-15", f"Ожидалась дата выезда 2025-01-15, но дата выезда '{updated_booking_data["bookingdates"]["checkout"]}'"
        assert updated_booking_data["additionalneeds"] == "Breakfast", f"Дополнительные условия ожидались Breakfast, но дополнительно '{updated_booking_data['depositpaid']}'"

    def test_partia_booking_update(self, auth_session, booking_data):
        """Тест на частичное обновление бронирования"""

        # Создаем бронирование
        create_booking_response = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking_response.status_code == 200, f"Error creating booking: {create_booking_response.status_code}, {create_booking_response.text}"

        create_booking_data = create_booking_response.json()
        booking_id = create_booking_data['bookingid']
        assert booking_id is not None, "Booking ID not found in the response"

        # Проверяем firstname, totalprice
        assert create_booking_data["booking"]["firstname"] == booking_data["firstname"], "Created firstname does not match"
        assert create_booking_data["booking"]["totalprice"] == booking_data["totalprice"], "Created totalprice does not match"

        # передаем данные для изменения
        partial_update_data = {
            "firstname": "Лариса",
            "additionalneeds": "Ужин"
        }

        # PATCH запрос
        update_url = f"{BASE_URL}/booking/{booking_id}"
        patch_booking_response = auth_session.patch(update_url, json=partial_update_data)
        assert patch_booking_response.status_code == 200, f"Ошибка: {patch_booking_response.status_code}, {patch_booking_response.text}"

        # Получаем бронирование
        get_booking_response = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking_response.status_code == 200, f"Ошибка: {get_booking_response.status_code}, {get_booking_response.text}"
        updated_booking_data = get_booking_response.json()

        # Проверяем изменение данных
        assert updated_booking_data['firstname'] == "Лариса", f"Ожидалось имя Лариса, но имя {updated_booking_data['firstname']}"
        assert updated_booking_data['additionalneeds'] == "Ужин", f"Ожидалось дополнительно Ужин, но дополнительно {updated_booking_data['additionalneeds']}"

        # Проверяем, что другие данные из первоначального бронирования не изменились
        assert updated_booking_data['lastname'] == booking_data['lastname'], f"Ожидалась фамилия 'Brown', но фамилия {updated_booking_data['lastname']}"
        assert updated_booking_data['totalprice'] == booking_data['totalprice'], f"Ожидалась цена 111, но цена {updated_booking_data['totalprice']}"

    def test_negativ_booking(self, auth_session, booking_data):
        """Тест на проверку кода 500 при пропуске обязательного поля"""

        data= {
            "firstname": "Лариса",
            "lastname": "Brown", # totalprice  не передан
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-04",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # POST запрос на создание бронирования
        response = auth_session.post(f"{BASE_URL}/booking", json=data)

        # Проверяем статус-код 400 (Bad Request)
        assert response.status_code == 500, f"Ожидался статус-код 500, но {response.status_code},{response.text}"

    def test_negativ_value_booking(self, auth_session, booking_data):
        """Тест на проверку кода 500 при неверном формате данных"""

        data= {
            "totalprice": "asjsdh", # totalprice передан текстом
            "depositpaid": True,
            "bookingdates": {
                "checkin": "",
                "checkout": ""
            },
            "additionalneeds": "Breakfast"
        }

        # POST запрос на создание бронирования
        response = auth_session.post(f"{BASE_URL}/booking", json=data)

        # Проверяем статус-код 400 (Bad Request)
        assert response.status_code == 400, f"Ожидался статус-код 400, но {response.status_code},{response.text}"


    def test_negativ_value_booking_1(self, auth_session, booking_data):
        """Тест на проверку кода 400 при неверном формате данных"""

        data = {
            "firstname": "11232251561541",
            "lastname": "325164646147+6768+817+8778",
            "totalprice": "asjsdh",  # totalprice передан текстом
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-04",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # POST запрос на создание бронирования
        response = auth_session.post(f"{BASE_URL}/booking", json=data)

        # Проверяем статус-код 400 (Bad Request)
        assert response.status_code == 400, f"Ожидался статус-код 400, но {response.status_code},{response.text}"

    def test_update_nonexistent_booking(self, auth_session):
        """Тест на попытку обновления несуществующего ресурса"""
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

        # Try PUT request
        put_url = f"{BASE_URL}/booking/{booking_id}"
        put_response = auth_session.put(put_url, json=data)
        assert put_response.status_code == 404, f"Ожидалась ошибка 404, но ошибка {put_response.status_code}, {put_response.text}"

        # Try PATCH request
        patch_url = f"{BASE_URL}/booking/{booking_id}"
        patch_data = {"firstname": "PartiallyUpdatedName"}  # Partial update data
        patch_response = auth_session.patch(patch_url, json=patch_data)
        assert patch_response.status_code == 405, f"Ожидалась ошибка 404, но ошибка {patch_response.status_code}, {patch_response.text}"

    def test_negativ_value_booking(self, auth_session, booking_data):
        """Тест на проверку кода 400 при передаче пустых данных"""

        data = {
            "firstname": "Лариса",
            "lastname": "Brown",
            "totalprice": "asjsdh",  # totalprice передан текстом
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-04",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # POST запрос на создание бронирования
        response = auth_session.post(f"{BASE_URL}/booking", json=data)

        # Проверяем статус-код 400 (Bad Request)
        assert response.status_code == 400, f"Ожидался статус-код 400, но {response.status_code},{response.text}"

    def test_with_empty_data(self, auth_session, booking_data):
        """Тест на проверку кода 400 при передаче пустых данных"""

        # Создаем бронирование
        create_booking_response = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking_response.status_code == 200, f"Error creating booking: {create_booking_response.status_code}, {create_booking_response.text}"

        create_booking_data = create_booking_response.json()
        booking_id = create_booking_data['bookingid']
        assert booking_id is not None, "Booking ID not found in the response"

        # Проверяем firstname, totalprice
        assert create_booking_data["booking"]["firstname"] == booking_data["firstname"], "Created firstname does not match"
        assert create_booking_data["booking"]["totalprice"] == booking_data["totalprice"], "Created totalprice does not match"

        # передаем данные для изменения
        partial_update_data = {
            "firstname": "",
            "additionalneeds": ""
        }

        # PATCH запрос
        update_url = f"{BASE_URL}/booking/{booking_id}"
        patch_booking_response = auth_session.patch(update_url, json=partial_update_data)
        assert patch_booking_response.status_code == 200, f"Ошибка: {patch_booking_response.status_code}, {patch_booking_response.text}"

        # Проверяем все данные бронирования
        assert partial_update_data['firstname'] == '', f"Ожидалось имя 'Jim', но имя '{partial_update_data['firstname']}'"
        assert partial_update_data["additionalneeds"] == "", f"Дополнительные условия ожидались Breakfast, но дополнительно '{partial_update_data['depositpaid']}'"

        data = {
            "firstname": "",
            "lastname": "",
            "totalprice": "1000",
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-01-04",
                "checkout": "2025-01-15"
            },
            "additionalneeds": "Breakfast"
        }

        # PUT запрос
        put_url = f"{BASE_URL}/booking/{booking_id}"
        put_response = auth_session.put(put_url, json=data)
        assert put_response.status_code == 200, f"Ожидалась ошибка 400, но ошибка {put_response.status_code}, {put_response.text}"




