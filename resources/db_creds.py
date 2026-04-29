import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class DBCreds:
    """Класс для хранения учетных данных для подключения к БД"""

    # Загружаем значения из переменных окружения
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    @classmethod
    def get_connection_params(cls):
        """Возвращает словарь с параметрами подключения"""
        return {
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
            "dbname": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD
        }

    @classmethod
    def get_connection_string(cls):
        """Возвращает строку подключения"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


# Для проверки, что креды загрузились (без пароля)
if __name__ == "__main__":
    print(f"Хост: {DBCreds.DB_HOST}")
    print(f"Порт: {DBCreds.DB_PORT}")
    print(f"Имя БД: {DBCreds.DB_NAME}")
    print(f"Пользователь: {DBCreds.DB_USER}")
    print(f"Пароль: {'*' * len(DBCreds.DB_PASSWORD) if DBCreds.DB_PASSWORD else 'Не установлен'}")