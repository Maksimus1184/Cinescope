
import pytest
import allure
import random
import time


@pytest.fixture  # была добавлена в файл conftest.py
def delay_between_retries():
    time.sleep(2)  # Задержка в 2 секунды\ это не обязательно но
    yield  # нужно понимать что такая возможность имеется


@allure.title("Тест с перезапусками")
@pytest.mark.flaky(reruns=3)
def test_with_retries(delay_between_retries):
    with allure.step("Шаг 1: Проверка случайного значения"):
        result = random.choice([True, False])
        assert result, "Тест упал, потому что результат False"