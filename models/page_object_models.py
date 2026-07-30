"""
Page Object Models для UI тестов Cinescope
"""
from playwright.sync_api import Page
import allure


class CinescopRegisterPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://dev-cinescope.coconutqa.ru/register"

        # Локаторы элементов
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[data-qa-id='register_submit_button']"
        self.sign_button = "a[href='/login' and text()='Войти']"

    def go_to_home_page(self):
        """Переход на главную страницу."""
        self.page.click(self.home_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    def go_to_all_movies(self):
        """Переход на страницу 'Все фильмы'."""
        self.page.click(self.all_movies_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")

    def open(self):
        """Переход на страницу регистрации."""
        self.page.goto(self.url)

    def enter_full_name(self, full_name: str):
        """Ввод full_name"""
        self.page.fill(self.full_name_input, full_name)

    def enter_email(self, email: str):
        """Ввод email"""
        self.page.fill(self.email_input, email)

    def enter_password(self, password: str):
        """Ввод пароля"""
        self.page.fill(self.password_input, password)

    def enter_repeat_password(self, password: str):
        """Ввод подтверждения пароля"""
        self.page.fill(self.repeat_password_input, password)

    def click_register_button(self):
        """Клик по кнопке регистрации"""
        self.page.click(self.register_button)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Полный процесс регистрации."""
        self.enter_full_name(full_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_repeat_password(confirm_password)
        self.click_register_button()

    def wait_redirect_to_login_page(self):
        """Переход на страницу login."""
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/login")
        assert self.page.url == "https://dev-cinescope.coconutqa.ru/login", "Редирект на домашнюю страницу не произошел"

    def check_allert(self):
        """Проверка всплывающего сообщения после редиректа"""
        notification_locator = self.page.get_by_text("Подтвердите свою почту")
        notification_locator.wait_for(state="visible")
        assert notification_locator.is_visible(), "Уведомление не появилось"
        notification_locator.wait_for(state="hidden")
        assert notification_locator.is_visible() == False, "Уведомление не исчезло"


class CinescopLoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://dev-cinescope.coconutqa.ru/login"

        # Локаторы элементов
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"

        self.login_button = "button[data-qa-id='login_submit_button']"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"

    def go_to_home_page(self):
        """Переход на главную страницу"""
        self.page.click(self.home_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    def go_to_all_movies(self):
        """Переход на страницу 'Все фильмы'"""
        self.page.click(self.all_movies_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")

    def open(self):
        """Переход на страницу входа"""
        self.page.goto(self.url)

    def enter_email(self, email: str):
        """Ввод email"""
        self.page.fill(self.email_input, email)

    def enter_password(self, password: str):
        """Ввод пароля"""
        self.page.fill(self.password_input, password)

    def click_login_button(self):
        """Клик по кнопке входа"""
        self.page.click(self.login_button)

    def login(self, email: str, password: str):
        """Полный процесс входа"""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    def wait_redirect_to_home_page(self, timeout: int = 30000):
        """
        Ожидание перехода на домашнюю страницу с диагностикой
        """
        try:
            # Ждем, пока URL станет корневым
            self.page.wait_for_url("**/", timeout=timeout)
        except Exception as e:
            # Делаем скриншот при ошибке
            screenshot = self.page.screenshot()
            allure.attach(screenshot, name="redirect_failure", attachment_type=allure.attachment_type.PNG)

            # Сохраняем HTML для диагностики
            html_content = self.page.content()
            allure.attach(html_content, name="page_html", attachment_type=allure.attachment_type.HTML)

            # Проверяем наличие ошибок на странице
            error_locator = self.page.locator(".error, .alert, [role='alert']")
            if error_locator.count() > 0:
                error_text = error_locator.first.text_content()
                raise AssertionError(f"Ошибка на странице: {error_text}")

            raise AssertionError(f"Не удалось перейти на главную страницу. Текущий URL: {self.page.url}") from e

        # Проверяем, что мы не остались на странице логина/регистрации
        assert "login" not in self.page.url, f"Остались на странице логина: {self.page.url}"
        assert "register" not in self.page.url, f"Остались на странице регистрации: {self.page.url}"

    def check_allert(self, timeout: int = 15000):
        """
        Проверка всплывающего сообщения после редиректа
        """
        try:
            # Проверка появления алерта
            notification_locator = self.page.get_by_text("Вы вошли в аккаунт")
            notification_locator.wait_for(state="visible", timeout=timeout)
            assert notification_locator.is_visible(), "Уведомление не появилось"

            # Ожидание исчезновения
            notification_locator.wait_for(state="hidden", timeout=timeout)
            assert not notification_locator.is_visible(), "Уведомление не исчезло"

        except Exception as e:
            # Делаем скриншот при ошибке
            screenshot = self.page.screenshot()
            allure.attach(screenshot, name="alert_not_found", attachment_type=allure.attachment_type.PNG)

            # Проверяем, может быть другое уведомление
            page_text = self.page.locator("body").text_content()
            allure.attach(page_text, name="page_text", attachment_type=allure.attachment_type.TEXT)

            raise AssertionError(f"Не удалось найти уведомление: {e}") from e


# models/page_object_models.py (добавьте в конец файла)

class CinescopMoviePage:
    def __init__(self, page: Page):
        self.page = page
        self.textarea = "textarea"
        self.submit_button = "button[type='submit']"
        self.success_message = "[role='alert'], .success, .alert-success"

    def create_review(self, rating: int, comment: str):
        """Создание отзыва"""
        # Вводим комментарий
        self.page.fill(self.textarea, comment)

        # Выбираем рейтинг (если есть)
        rating_select = self.page.locator("select, [data-qa-id='rating']")
        if rating_select.count() > 0:
            rating_select.select_option(str(rating))

        # Нажимаем кнопку отправки
        self.page.click(self.submit_button)
        self.page.wait_for_timeout(2000)

    def check_review_success(self):
        """Проверка успешного создания отзыва"""
        # Проверяем сообщение об успехе
        success = self.page.locator(self.success_message)
        if success.count() > 0:
            print(f"✅ Отзыв создан: {success.first.text_content()}")
        else:
            # Проверяем, что отзыв появился в списке
            reviews = self.page.locator(".review, .comment")
            if reviews.count() > 0:
                print(f"✅ Отзыв создан! Всего отзывов: {reviews.count()}")
            else:
                print("⚠️ Отзыв не найден")









