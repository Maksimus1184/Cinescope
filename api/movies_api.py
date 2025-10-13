from custom_requester.custom_requester import CustomRequester
from constants import MOVIES_ENDPOINT

class MoviesAPI(CustomRequester):
    def __init__(self, session, base_url):
        super().__init__(session=session, base_url=base_url)
        self.session = session

    def create_movie(self, movie_data, expected_status=201):
        """ Создание нового фильма"""
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT,
            json=movie_data,
            expected_status=expected_status
        )

    def get_movies(self, params=None, expected_status=200):
        """
        Получаем список фильмов
        """
        return self.send_request(
            method="GET",
            endpoint=MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        """
        Получаем фильм по ID
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удаление фильма
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )

    def update_movie(self, movie_id, update_data, expected_status=200):
        """
        Редактирование фильма по ID
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            json=update_data,
            expected_status=expected_status
        )



