from custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):
    def __init__(self, session, base_url):
        super().__init__(session=session, base_url=base_url)
        self.session = session

    def get_user_info(self, user_id, expected_status=200):
        """
        Получение информации о пользователе.
        """
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):
        """
        Удаление пользователя.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def get_user(self, user_locator, expected_status=200):  # Добавьте expected_status
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_locator}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint="/user",
            json=user_data,
            expected_status=expected_status
        )
