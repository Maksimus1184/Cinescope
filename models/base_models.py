from pydantic import BaseModel, Field, field_validator
from typing import Optional
import datetime
import re
from typing import List
from pydantic import BaseModel, Field, field_validator
from enums.enums import Roles



class TestUser(BaseModel):
    id: Optional[str] = None  # Добавляем опциональное поле id
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="passwordRepeat должен вполностью совпадать с полем password")
    roles: List[str]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    class Config:
        json_encoders = {
            Roles: lambda v: v.value
        }

# Добавим модель для логина
class LoginRequest(BaseModel):
    email: str
    password: str

# models/base_models.py (добавляем)
class LoginResponse(BaseModel):
    accessToken: str
    user: dict  # или можно создать вложенную модель, но для простоты оставим dict
    expiresIn: int  # из логов видно, что есть expiresIn

class ErrorResponse(BaseModel):
    message: str
    error: str
    statusCode: int

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: bool
    roles: List[str]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value


class CreateUserResponse(BaseModel):
    id: str
    email: str
    fullName: str
    roles: List[str]
    verified: bool
    banned: bool
    createdAt: str  # если есть в ответе

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты")
        return value