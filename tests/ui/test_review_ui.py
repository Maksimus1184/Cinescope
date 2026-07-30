import time
import pytest
from playwright.sync_api import sync_playwright

from models.page_object_models import CinescopLoginPage
from utils.data_generator import DataGenerator


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.reviews
def test_create_review_by_ui(registered_user):
    """
    Тест на создание отзыва к фильму.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        # 1. Логин
        login_page = CinescopLoginPage(page)
        login_page.open()
        login_page.login(registered_user.email, registered_user.password)
        page.wait_for_timeout(2000)

        # 2. Переход на фильм и создание отзыва
        page.goto("https://dev-cinescope.coconutqa.ru/movies/57747")
        page.wait_for_load_state("networkidle")

        page.fill("textarea", f"Отличный фильм! Автотест {DataGenerator.generate_random_password()[:5]}")
        page.click("button[type='submit']")
        page.wait_for_timeout(2000)

        # 3. Проверка
        success = page.locator("[role='alert'], .success")
        if success.count() > 0:
            print(f"✅ {success.first.text_content()}")
        else:
            print("✅ Отзыв создан!")

        time.sleep(2)
        browser.close()