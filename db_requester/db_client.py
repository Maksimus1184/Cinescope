from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.db_creds import DBCreds

# ИСПРАВЛЕНО: используем правильные поля
USERNAME = DBCreds.DB_USER  # <-- ИЗМЕНЕНО: DB_USER, а не DB_NAME
PASSWORD = DBCreds.DB_PASSWORD
HOST = DBCreds.DB_HOST
PORT = DBCreds.DB_PORT
DATABASE_NAME = DBCreds.DB_NAME  # это правильно

print(f"Подключение к БД: {USERNAME}@{HOST}:{PORT}/{DATABASE_NAME}")  # для отладки

# движок для подключения к базе данных
engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False  # Установить True для отладки SQL запросов
)

# создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()