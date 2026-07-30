
from sqlalchemy.orm import Session
from db_models.user import UserDBModel
from db_models.movie import MovieDBModel


class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """Класс с методами для работы с БД в тестах"""

    # ===== Методы для пользователей =====
    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    # ===== Методы для работы с фильмами =====
    def create_test_movie(self, movie_data: dict) -> MovieDBModel:
        """
        Создает тестовый фильм в БД

        Args:
            movie_data: словарь с данными фильма

        Returns:
            MovieDBModel: созданный объект фильма
        """
        movie = MovieDBModel(**movie_data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def get_movie_by_id(self, movie_id: str) -> MovieDBModel:
        """
        Получает фильм по ID

        Args:
            movie_id: UUID фильма

        Returns:
            MovieDBModel или None, если фильм не найден
        """
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.id == movie_id
        ).first()

    def get_movie_by_name(self, name: str) -> MovieDBModel:
        """
        Получает фильм по названию

        Args:
            name: название фильма

        Returns:
            MovieDBModel или None, если фильм не найден
        """
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.name == name
        ).first()

    def movie_exists_by_name(self, name: str) -> bool:
        """
        Проверяет существование фильма по названию

        Args:
            name: название фильма

        Returns:
            bool: True если фильм существует
        """
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.name == name
        ).count() > 0

    def movie_exists_by_id(self, movie_id: str) -> bool:
        """
        Проверяет существование фильма по ID

        Args:
            movie_id: UUID фильма

        Returns:
            bool: True если фильм существует
        """
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.id == movie_id
        ).count() > 0

    def delete_movie(self, movie: MovieDBModel):
        """
        Удаляет фильм из БД

        Args:
            movie: объект фильма для удаления
        """
        self.db_session.delete(movie)
        self.db_session.commit()

    def delete_movie_by_id(self, movie_id: str):
        """
        Удаляет фильм по ID

        Args:
            movie_id: UUID фильма для удаления
        """
        movie = self.get_movie_by_id(movie_id)
        if movie:
            self.db_session.delete(movie)
            self.db_session.commit()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    # ===== НОВЫЙ МЕТОД =====
    def get_first_movie(self):
        """
        Получает первый фильм из БД

        Returns:
            MovieDBModel или None, если фильмов нет
        """
        return self.db_session.query(MovieDBModel).first()