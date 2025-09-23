import pytest
import requests
from faker import Faker
from constants import HEADERS, BASE_URL

faker = Faker()

@pytest.fixture(scope="session")
def auth_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    response = requests.post(
        f"{BASE_URL}/auth",
        headers=HEADERS,
        json={"username": "admin", "password": "password123"}
    )
    assert response.status_code == 200, "Ошибка авторизации"
    token = response.json().get("token")
    assert token is not None, "В ответе не оказалось токена"

    session.headers.update({"Cookie": f"token={token}"})
    return session

@pytest.fixture
def booking_data():
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
    """Creates a booking and returns the booking ID.  Deletes the booking after the test."""
    response = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
    assert response.status_code == 200, f"Failed to create booking: {response.status_code} - {response.text}"
    booking_id = response.json().get("bookingid")
    assert booking_id is not None, "Booking ID not found in create response"

    yield booking_id