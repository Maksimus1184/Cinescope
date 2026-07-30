# tests/ui/test_review_ui.py

import time
from playwright.sync_api import sync_playwright

from models.page_object_models import CinescopLoginPage, CinescopMoviePage
from utils.data_generator import DataGenerator


def test_create_review_by_ui():
    with sync_playwright() as playwright:
        # Генерируем данные для пользователя
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        # Запуск браузера
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        # Создаем объекты страниц
        login_page = CinescopLoginPage(page)
        movie_page = CinescopMoviePage(page)

        # 1. Регистрация пользователя
        register_page = CinescopRegisterPage(page)
        register_page.open()
        register_page.register(random_name, random_email, random_password, random_password)
        register_page.wait_redirect_to_login_page()
        register_page.check_allert()

        # 2. Логин
        login_page.open()
        login_page.login(random_email, random_password)
        login_page.wait_redirect_to_home_page()
        login_page.check_allert()

        # 3. Переход на страницу фильма
        MOVIE_ID = 57747  # Фильм "Бенджамин Принс" с формой отзыва
        page.goto(f"https://dev-cinescope.coconutqa.ru/movies/{MOVIE_ID}")
        page.wait_for_load_state("networkidle")

        # 4. Создание отзыва
        movie_page.create_review(
            rating=5,
            comment=f"Отличный фильм! Автотест {random.randint(1, 999)}"
        )

        # 5. Проверка успешного создания
        movie_page.check_review_success()

        # Пауза для визуальной проверки
        time.sleep(3)

        # Закрываем браузер
        browser.close()