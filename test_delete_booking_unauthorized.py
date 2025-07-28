import pytest
import requests
from faker import Faker
from constants import HEADERS, BASE_URL

faker = Faker()

@pytest.fixture(scope="session")
def auth_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    response = session.post(
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

    yield booking_id # Return the booking ID

    # Teardown: Delete the booking
    delete_url = f"{BASE_URL}/booking/{booking_id}"
    delete_response = auth_session.delete(delete_url)
    assert delete_response.status_code == 204, f"Failed to delete booking {booking_id} after the test: {delete_response.status_code}, {delete_response.text}"

class TestDeleteUnauthorized:

    def test_delete_booking_unauthorized(self, create_booking):
        """
        Tests that attempting to delete a booking without authorization returns
        a 401 Unauthorized or 403 Forbidden status code.
        """
        booking_id = create_booking  # Get the booking ID from the fixture

        # Create a new session without authorization
        unauth_session = requests.Session()
        unauth_session.headers.update(HEADERS)  # Keep existing headers, but NO Cookie

        delete_url = f"{BASE_URL}/booking/{booking_id}"
        response = unauth_session.delete(delete_url)

        # Assert that the status code is 401 or 403
        assert response.status_code in (401, 403), f"Expected 401 or 403, got {response.status_code}, {response.text}"

        try:
            response_json = response.json()
            print(f"Response (JSON): {response_json}")
        except requests.exceptions.JSONDecodeError:
            print(f"Response (non-JSON): {response.text}")