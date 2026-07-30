# models/base_models.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re
import datetime


class TestUser(BaseModel):
    """Модель тестового пользователя для регистрации"""
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: List[str] = ["USER"]
    # Поля ниже нужны только для ответа от API, не для отправки
    id: Optional[str] = None
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Неверный формат email")
        return v


class LoginRequest(BaseModel):
    """Модель запроса для логина"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Модель ответа для логина"""
    accessToken: str
    user: dict
    expiresIn: int


class ErrorResponse(BaseModel):
    """Модель ответа с ошибкой"""
    message: str
    error: str
    statusCode: int


class RegisterUserResponse(BaseModel):
    """Модель ответа для регистрации"""
    id: str
    email: str
    fullName: str
    verified: bool
    roles: List[str]
    createdAt: str
    # Делаем banned опциональным, так как API может не возвращать его
    banned: Optional[bool] = None

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени")
        return value


class CreateUserResponse(BaseModel):
    """Модель ответа для создания пользователя"""
    id: str
    email: str
    fullName: str
    roles: List[str]
    verified: bool
    banned: Optional[bool] = None
    createdAt: str

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты")
        return value