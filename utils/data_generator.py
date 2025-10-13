import random
import string
from faker import Faker

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

