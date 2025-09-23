import pytest
import requests
from faker import Faker
from constants import HEADERS, BASE_URL

faker = Faker()


def test_delete_booking_unauthorized(create_booking):

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
