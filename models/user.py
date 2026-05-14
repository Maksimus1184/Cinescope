"""
Pydantic модели для User API
"""
from pydantic import BaseModel
from typing import Optional


class UserResponse(BaseModel):
    """Модель ответа для пользователя"""
    id: int
    email: str
    name: str
    role: str  # admin, user и т.д.


class LoginRequest(BaseModel):
    """Модель запроса для логина"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Модель ответа для логина"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse