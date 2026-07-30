"""
Генератор тестовых данных
"""
import random
import string
import re
import time


class DataGenerator:
    """Генератор тестовых данных"""

    @staticmethod
    def generate_random_email() -> str:
        """Генерация случайного email"""
        domains = ["gmail.com", "mail.ru", "yandex.ru", "test.com"]
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(domains)
        return f"{name}@{domain}"

    @staticmethod
    def generate_random_name() -> str:
        """Генерация случайного имени"""
        first_names = ["John", "Jane", "Alex", "Maria", "Michael", "Sarah", "David", "Emma"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        Генерация пароля, соответствующего требованиям API
        """
        special_chars = "?@#$%^&*_\\-+()[]{}><\\\\/\\|\"'.,:;"
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZабвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        all_allowed = letters + string.digits + special_chars

        password = []
        password.append(random.choice(letters))
        password.append(random.choice(string.digits))

        remaining = length - 2
        if remaining > 0:
            password.extend(random.choices(all_allowed, k=remaining))

        random.shuffle(password)
        result = ''.join(password)[:20]

        while len(result) < 8:
            result += random.choice(all_allowed)

        pattern = r'^(?=.*[a-zA-Zа-яА-Я])(?=.*\d)[a-zA-Zа-яА-Я\d?@#$%^&*_\-+()\[\]{}><\\/\\|"\'.,:;]{8,20}$'
        if not re.match(pattern, result):
            return DataGenerator.generate_random_password(length)

        return result

    @staticmethod
    def generate_movie_title() -> str:
        """Генерация уникального названия фильма"""
        adjectives = ["Great", "Amazing", "Wonderful", "Incredible", "Fantastic", "Epic", "Brilliant", "Magnificent"]
        nouns = ["Movie", "Story", "Adventure", "Journey", "Tale", "Saga", "Quest", "Dream"]
        timestamp = int(time.time() * 1000) % 100000
        return f"The {random.choice(adjectives)} {random.choice(nouns)} {timestamp}"

    @staticmethod
    def generate_image_url() -> str:
        """Генерация URL изображения"""
        return f"https://cdn.movies.com/posters/movie_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}.jpg"

    @staticmethod
    def generate_price() -> int:
        """Генерация цены"""
        return random.randint(50, 1000)

    @staticmethod
    def generate_description() -> str:
        """Генерация описания"""
        phrases = [
            "Great movie", "Amazing story", "Beautiful cinematography",
            "Must watch", "Incredible performance", "Stunning visuals",
            "Heartwarming tale", "Action-packed adventure", "Thought-provoking drama"
        ]
        description = " ".join(random.choices(phrases, k=random.randint(2, 4)))
        if len(description) > 200:
            description = description[:197] + "..."
        return description

    @staticmethod
    def generate_location() -> str:
        """Генерация локации"""
        return random.choice(["MSK", "SPB"])

    @staticmethod
    def generate_genre_id() -> int:
        """Генерация ID жанра - только рабочие ID"""
        # Исключаем проблемные: 1, 3, 5
        working_genres = [4, 6, 7, 8, 9, 10]
        return random.choice(working_genres)

    @staticmethod
    def generate_rating() -> float:
        """Генерация рейтинга (0-5)"""
        return round(random.uniform(0, 5), 1)

    @staticmethod
    def generate_movie_data() -> dict:
        """Генерация данных для фильма"""
        return {
            "name": DataGenerator.generate_movie_title(),
            "imageUrl": DataGenerator.generate_image_url(),
            "price": DataGenerator.generate_price(),
            "description": DataGenerator.generate_description(),
            "location": DataGenerator.generate_location(),
            "published": True,
            "genreId": DataGenerator.generate_genre_id(),
            "rating": DataGenerator.generate_rating()
        }

    @staticmethod
    def generate_user_data() -> dict:
        """Генерация данных для пользователя"""
        return {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": DataGenerator.generate_random_password(),
            "roles": ["USER"]
        }


# Тест для проверки генератора
if __name__ == "__main__":
    # Проверяем генерацию паролей
    for i in range(5):
        password = DataGenerator.generate_random_password()
        pattern = r'^(?=.*[a-zA-Zа-яА-Я])(?=.*\d)[a-zA-Zа-яА-Я\d?@#$%^&*_\-+()\[\]{}><\\/\\|"\'.,:;]{8,20}$'
        assert re.match(pattern, password), f"Пароль {password} не соответствует требованиям"
    print("✅ Все пароли валидны!")

    # Проверяем генерацию данных для фильма
    movie = DataGenerator.generate_movie_data()
    print(f"\nДанные для фильма: {movie}")
    assert "rating" in movie, "❌ rating отсутствует!"
    assert 0 <= movie["rating"] <= 5, f"❌ rating {movie['rating']} вне диапазона!"
    assert movie["genreId"] not in [1, 3, 5], f"❌ genreId {movie['genreId']} проблемный!"
    print("✅ Все данные для фильма корректны!")