from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from utils.data_generator import DataGenerator
import pytest
import allure
from typing import Dict, Any

# Подключение к базе данных
host = "80.90.191.123"
port = 31200
database_name = "db_movies"
username = "postgres"
password = "AmwFrtnR2"

# формируем урл для подключения к базе
connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}"
# объект для подключения к базе данных
engine = create_engine(connection_string)

# Базовый класс для моделей
Base = declarative_base()


# ============= МОДЕЛИ =============
class AccountTransactionTemplate(Base):
    """Модель для тестирования транзакций"""
    __tablename__ = 'accounts_test'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    balance = Column(Integer)


class MovieDBModel(Base):
    """Модель фильма"""
    __tablename__ = 'movies'

    id = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)
    location = Column(String)
    published = Column(Boolean)
    rating = Column(Float)
    genre_id = Column(String)
    created_at = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<Movie(id='{self.id}', name='{self.name}', price={self.price})>"


# ============= ТЕСТЫ =============
def test_connection():
    """Тест подключения к БД"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
        print("✓ Подключение к БД работает")


def test_sdl_alchemy_ORM():
    """Тест ORM запроса для пользователей"""
    # Базовый класс для моделей
    Base = declarative_base()

    # Модель таблицы users
    class User(Base):
        __tablename__ = 'users'
        id = Column(String, primary_key=True)
        email = Column(String)
        full_name = Column(String)
        password = Column(String)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
        verified = Column(Boolean)
        banned = Column(Boolean)
        roles = Column(String)

    # Создаем сессию
    Session = sessionmaker(bind=engine)
    session = Session()

    user_id = "3a172562-e05d-4768-82dd-a098d8e7bbb3"

    # Выполняем запрос
    user = session.query(User).filter(User.id == user_id).first()

    # Выводим результат
    if user:
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.full_name}")
    else:
        print("Пользователь не найден.")


def test_db_requests(super_admin, db_helper, created_test_user):
    """Тест для проверки работы с БД"""
    assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
    assert db_helper.user_exists_by_email("api1@gmail.com") is True
    print("✓ Тест DBHelper пройден")


class TestMovieAPIWithDB:
    """
    Тест для проверки создания и удаления фильма через API
    с проверкой состояния базы данных
    """

    def test_create_and_delete_movie_api_db_check(self, authorized_api_manager, db_helper):
        """
        Тест проверяет:
        1. До начала тестирования в базе отсутствует фильм
        2. После вызова запроса на создание в базе появился фильм
        3. После удаления фильма через API в базе также удаляется данный объект
        """
        # 1. Генерируем данные для фильма
        movie_data = DataGenerator.generate_movie_data()
        movie_name = movie_data['name']

        # 2. СОЗДАЕМ КОПИЮ ДАННЫХ ДЛЯ API
        api_movie_data = movie_data.copy()
        api_movie_data.pop('id', None)

        # 3. КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ ФОРМАТА
        if not api_movie_data['createdAt'].endswith('Z'):
            api_movie_data['createdAt'] = api_movie_data['createdAt'] + 'Z'
        api_movie_data.pop('imageUrl', None)

        print(f"\nСоздание фильма: {movie_name}")
        print(f"Данные для API: {api_movie_data}")

        # 4. Проверяем, что фильма нет в БД до теста
        assert not db_helper.movie_exists_by_name(movie_name), \
            f"Фильм '{movie_name}' уже существует в БД до начала теста"

        # 5. СОЗДАЕМ ФИЛЬМ ЧЕРЕЗ API
        response = authorized_api_manager.movies_api.create_movie(
            movie_data=api_movie_data,
            expected_status=201
        )

        created_movie_id = response.json().get('id')
        assert created_movie_id is not None, "В ответе API отсутствует ID созданного фильма"
        print(f"✓ Фильм создан, ID: {created_movie_id}")

        # 6. Проверяем, что фильм появился в БД
        assert db_helper.movie_exists_by_id(created_movie_id), \
            f"Фильм с ID {created_movie_id} не найден в БД"

        db_movie = db_helper.get_movie_by_id(created_movie_id)
        assert db_movie.name == movie_name, "Название фильма не совпадает"
        assert db_movie.price == api_movie_data['price'], "Цена фильма не совпадает"
        assert db_movie.location == api_movie_data['location'], "Локация не совпадает"
        assert db_movie.genre_id == api_movie_data['genreId'], "ID жанра не совпадает"
        print(f"✓ Фильм найден в БД: {db_movie.name}")

        # 7. Удаляем фильм через API
        delete_response = authorized_api_manager.movies_api.delete_movie(
            movie_id=created_movie_id,
            expected_status=[200, 204]
        )
        print(f"✓ Фильм удален через API, статус: {delete_response.status_code}")

        # 8. Проверяем, что фильм удален из БД
        assert not db_helper.movie_exists_by_id(created_movie_id), \
            f"Фильм с ID {created_movie_id} все еще существует в БД"
        assert not db_helper.movie_exists_by_name(movie_name), \
            f"Фильм с названием '{movie_name}' все еще существует в БД"

        print("✓ Тест создания/удаления фильма пройден")


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:
    """Тесты для проверки транзакций между счетами"""

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session: Session):
        # ====================================================================== Подготовка к тесту
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            # Создаем таблицу, если её нет
            Base.metadata.create_all(bind=engine, tables=[AccountTransactionTemplate.__table__])

            stan = AccountTransactionTemplate(
                user=f"Stan_{DataGenerator.generate_random_int(10)}",
                balance=1000
            )
            bob = AccountTransactionTemplate(
                user=f"Bob_{DataGenerator.generate_random_int(10)}",
                balance=500
            )
            db_session.add_all([stan, bob])
            db_session.commit()

            allure.attach(
                f"Stan: {stan.balance}, Bob: {bob.balance}",
                name="Начальные балансы",
                attachment_type=allure.attachment_type.TEXT
            )

        # Функция перевода денег (без декоратора allure.step на функции)
        def transfer_money(session, from_account, to_account, amount):
            # Получаем счета
            with allure.step(f"Получение счета отправителя: {from_account}"):
                from_obj = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()

            with allure.step(f"Получение счета получателя: {to_account}"):
                to_obj = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step(f"Проверка достаточности средств на счете {from_account}"):
                if from_obj.balance < amount:
                    raise ValueError(f"Недостаточно средств на счете {from_account}: {from_obj.balance} < {amount}")
                allure.attach(
                    f"Баланс отправителя: {from_obj.balance}, требуется: {amount}",
                    name="Проверка средств",
                    attachment_type=allure.attachment_type.TEXT
                )

            with allure.step(f"Выполнение перевода {amount} от {from_account} к {to_account}"):
                from_obj.balance -= amount
                to_obj.balance += amount

            with allure.step("Сохранение изменений в базе данных"):
                session.commit()

            return from_obj, to_obj

        # ====================================================================== Тест
        with allure.step("Проверка начальных балансов"):
            assert stan.balance == 1000, f"Stan: ожидалось 1000, получено {stan.balance}"
            assert bob.balance == 500, f"Bob: ожидалось 500, получено {bob.balance}"

        try:
            with allure.step("Выполнение перевода 200 единиц от Stan к Bob"):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            with allure.step("Проверка балансов после перевода"):
                # Обновляем объекты из БД
                db_session.refresh(stan)
                db_session.refresh(bob)

                assert stan.balance == 800, f"Stan: ожидалось 800, получено {stan.balance}"
                assert bob.balance == 700, f"Bob: ожидалось 700, получено {bob.balance}"

                allure.attach(
                    f"Stan: {stan.balance}, Bob: {bob.balance}",
                    name="Балансы после перевода",
                    attachment_type=allure.attachment_type.TEXT
                )

                allure.attach(
                    f"Суммарный баланс: {stan.balance + bob.balance}",
                    name="Общий баланс системы",
                    attachment_type=allure.attachment_type.TEXT
                )

        except Exception as e:
            with allure.step("Ошибка при переводе: откат транзакции"):
                db_session.rollback()
                allure.attach(
                    str(e),
                    name="Ошибка выполнения",
                    attachment_type=allure.attachment_type.TEXT
                )
            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаление тестовых данных из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()  # <-- ИСПРАВЛЕНО: убрана точка

                allure.attach(
                    "Тестовые данные успешно очищены",
                    name="Очистка",
                    attachment_type=allure.attachment_type.TEXT
                )

                print("✓ Тест транзакции пройден успешно")