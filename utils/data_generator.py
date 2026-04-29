import random
import string
from faker import Faker
import datetime
from uuid import uuid4

faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)  # Остальная длина пароля (минимум 8, максимум 20)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_movie_title():
        # Генерируем название фильма (например, "The Secret of XXXXXX")
        adjective = faker.word().capitalize()
        noun = faker.word().capitalize()
        return f"The {adjective} of {noun} #{random.randint(100, 999)}"

    @staticmethod
    def generate_image_url():
        # Генерируем URL, имитирующий изображение
        unique_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"https://cdn.movies.com/posters/movie_{unique_part}.jpg"

    @staticmethod
    def generate_price():
        # Цена от 1 до 1000
        return random.randint(1, 1000)

    @staticmethod
    def generate_description():
        # Генерируем несколько предложений для описания
        return faker.paragraph(nb_sentences=3)

    @staticmethod
    def generate_location():
        # Случайный выбор из известных локаций
        locations = ["SPB", "MSK"]
        return random.choice(locations)

    @staticmethod
    def generate_user_data() -> dict:
        """Генерирует данные для тестового пользователя"""
        return {
            'id': str(uuid4()),  # генерируем UUID как строку
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }

    @staticmethod
    def generate_movie_data() -> dict:
        """
        Генерирует данные для тестового фильма
        """
        unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Список существующих ID жанров (нужно узнать из документации или БД)
        # Судя по ответу API, есть жанр с id 3 ("Фантастика")
        existing_genre_ids = [3]

        return {
            'id': str(uuid4()),
            'name': f"Test Movie {unique_id}",
            'description': faker.paragraph(nb_sentences=3),
            'price': random.randint(10, 100),
            'imageUrl': f"https://test-cdn.com/movies/{unique_id}.jpg",
            'location': random.choice(["SPB", "MSK"]),
            'published': True,
            'createdAt': datetime.datetime.now().isoformat(),
            'rating': round(random.uniform(1.0, 10.0), 1),
            'genreId': random.choice(existing_genre_ids)  # <-- ИЗМЕНЕНО: теперь число
        }

    @staticmethod
    def generate_movie_data_with_params(**kwargs) -> dict:
        """
        Генерирует данные фильма с возможностью переопределить параметры

        Args:
            **kwargs: параметры для переопределения

        Returns:
            dict: словарь с данными фильма
        """
        movie_data = DataGenerator.generate_movie_data()
        movie_data.update(kwargs)  # переопределяем переданные параметры
        return movie_data

    @staticmethod
    def generate_random_int(length: int) -> int:
        """
        Генерирует случайное число заданной длины
        Например: generate_random_int(5) -> 12345
        """
        import random
        import string

        # Генерируем случайное число указанной длины
        min_value = 10 ** (length - 1)
        max_value = (10 ** length) - 1
        return random.randint(min_value, max_value)

    @staticmethod
    def generate_random_string(length: int) -> str:
        """Генерирует случайную строку"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

