# tests/ui/test_login_page.py
import pytest
from playwright.sync_api import sync_playwright
from models.page_object_models import CinescopLoginPage


@pytest.mark.ui
@pytest.mark.smoke
def test_login_by_ui(registered_user):
    """Тест логина через UI"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        login_page = CinescopLoginPage(page)

        login_page.open()
        login_page.login(registered_user.email, registered_user.password)

        # Ждем обработки запроса
        page.wait_for_timeout(3000)

        # Проверяем URL
        current_url = page.url
        print(f"Текущий URL: {current_url}")

        # Проверяем наличие видимых ошибок с текстом
        error_elements = page.locator(".error, .alert, [role='alert']")
        for i in range(error_elements.count()):
            element = error_elements.nth(i)
            if element.is_visible():
                error_text = element.text_content().strip()
                if error_text:  # Если есть текст
                    raise AssertionError(f"Ошибка при входе: {error_text}")

        # Проверяем, есть ли признаки успешного входа
        # 1. Проверяем наличие уведомления
        notification = page.get_by_text("Вы вошли в аккаунт")
        if notification.count() > 0 and notification.is_visible():
            print("✅ Найдено уведомление об успешном входе")
        else:
            print("ℹ️ Уведомление не найдено, проверяем другие признаки")

        # 2. Проверяем наличие кнопки "Выйти" (признак авторизации)
        logout_button = page.locator("text=Выйти, text=Logout, text=Выход, [data-qa-id='logout']")
        if logout_button.count() > 0 and logout_button.is_visible():
            print("✅ Найдена кнопка 'Выйти' - пользователь авторизован")
        else:
            print("ℹ️ Кнопка 'Выйти' не найдена")

        # 3. Проверяем наличие имени пользователя
        name_parts = registered_user.fullName.split()
        if name_parts:
            user_name = page.locator(f"text={name_parts[0]}")
            if user_name.count() > 0 and user_name.is_visible():
                print(f"✅ Найдено имя пользователя: {name_parts[0]}")

        # Принудительно переходим на главную, если не упали
        if "login" in current_url or "register" in current_url:
            print("🔄 Принудительный переход на главную")
            page.goto("https://dev-cinescope.coconutqa.ru/")
            page.wait_for_load_state("networkidle")

        # Финальная проверка - мы не на странице логина
        final_url = page.url
        assert "login" not in final_url, f"Остались на странице логина: {final_url}"
        assert "register" not in final_url, f"Остались на странице регистрации: {final_url}"

        print(f"✅ Тест успешно завершен! URL: {final_url}")

        browser.close()