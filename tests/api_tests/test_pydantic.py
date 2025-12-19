import pytest
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import logging

class RegistrationUserData(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: list
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')
        return v

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @model_validator(mode='after')
    def passwords_match(self) -> 'RegistrationUserData':
        if self.password != self.passwordRepeat:
            raise ValueError('Пароли не совпадают')
        return self


def test_registration_user_data(test_user):
    try:
        user = RegistrationUserData(**test_user)
        json_data = user.model_dump_json(exclude_unset=True)
        logging.info(f"JSON (exclude_unset=True): {json_data}")
        assert user.email == test_user["email"]

        logging.info(
            f"Данные пользователя: "
            f"email={user.email}, "
            f"fullName={user.fullName}, "
            f"password={user.password}, "
            f"passwordRepeat={user.passwordRepeat}, "
            f"roles={user.roles}"
        )
        return True
    except Exception as e:
        logging.error(f"Ошибка валидации: {e}")
        return False

def test_creation_user_data(creation_user_data):
    try:
        user = RegistrationUserData(**creation_user_data)
        json_data = user.model_dump_json()
        logging.info(f"JSON: {json_data}")
        assert user.email == creation_user_data["email"]

        logging.info(
            f"Данные пользователя: "
            f"email={user.email}, "
            f"fullName={user.fullName}, "
            f"password={user.password}, "
            f"passwordRepeat={user.passwordRepeat}, "
            f"roles={user.roles}"
        )
        return True
    except Exception as e:
        logging.error(f"Ошибка валидации: {e}")
        return False


# Тестовые данные
VALID_DATA_1 = {
    "email": "test.user@example.com",
    "fullName": "Иван Иванов",
    "password": "StrongPass123",
    "passwordRepeat": "StrongPass123",
    "roles": ["USER", "ADMIN"],
    "banned": False,
    "verified": True
}

INVALID_EMAIL = {
    "email": "invalid-email.com",
    "fullName": "Тест",
    "password": "Password123",
    "passwordRepeat": "Password123",
    "roles": ["USER"]
}

MISMATCHED_PASSWORDS = {
    "email": "user@test.com",
    "fullName": "Несовпадающие пароли",
    "password": "FirstPassword123",
    "passwordRepeat": "DifferentPassword456",
    "roles": ["USER"]
}

SHORT_PASSWORD = {
    "email": "user@test.com",
    "fullName": "Короткий пароль",
    "password": "short7",
    "passwordRepeat": "short7",
    "roles": ["USER"]
}


# ТЕСТЫ

def test_valid_data():
    """Тест с корректными данными"""
    user = RegistrationUserData(**VALID_DATA_1)
    assert user.email == VALID_DATA_1["email"]
    assert user.fullName == VALID_DATA_1["fullName"]
    assert user.password == VALID_DATA_1["password"]


def test_invalid_email():
    """Тест с некорректным email (без @)"""
    with pytest.raises(ValueError, match="Email must contain @ symbol"):
        RegistrationUserData(**INVALID_EMAIL)


def test_mismatched_passwords():
    """Тест с несовпадающими паролями"""
    with pytest.raises(ValueError, match="Пароли не совпадают"):
        RegistrationUserData(**MISMATCHED_PASSWORDS)


def test_short_password():
    """Тест с коротким паролем"""
    with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
        RegistrationUserData(**SHORT_PASSWORD)


def test_missing_required_field():
    """Тест с отсутствующим обязательным полем"""
    incomplete_data = {
        "email": "test@example.com",
        "password": "Password123",
        "passwordRepeat": "Password123",
        "roles": ["USER"]
    }
    with pytest.raises(Exception):
        RegistrationUserData(**incomplete_data)





