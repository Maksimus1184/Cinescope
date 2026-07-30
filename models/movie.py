"""
Pydantic модели для Movie API
Адаптированы под реальный API (который не соответствует Swagger)
"""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, validator, field_validator
import logging


class Genre(BaseModel):
    """Модель жанра - реальное API возвращает только name"""
    id: Optional[int] = None  # API не возвращает id!
    name: str


class Review(BaseModel):
    """Модель отзыва"""
    id: int
    movieId: int
    userId: int
    rating: int
    comment: str
    createdAt: datetime


class MovieResponse(BaseModel):
    """
    Модель ответа для одного фильма
    Адаптирована под РЕАЛЬНЫЙ API (баг: не соответствует Swagger)
    """
    id: int
    name: str
    imageUrl: Optional[str] = None  # БАГ: в БД есть null, хотя Swagger требует string
    price: int
    description: str
    location: str
    published: bool
    genreId: int
    createdAt: datetime
    rating: float
    reviews: List[Review] = []
    genre: Optional[Genre] = None  # БАГ: API возвращает без id

    @validator('price')
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('price must be positive')
        return v

    @validator('location')
    def location_must_be_valid(cls, v):
        if v not in ['MSK', 'SPB']:
            raise ValueError('location must be MSK or SPB')
        return v

    class Config:
        from_attributes = True
        extra = "ignore"  # Игнорируем лишние поля


class MoviesListResponse(BaseModel):
    """
    Модель ответа для списка фильмов
    Адаптирована под РЕАЛЬНЫЙ API
    """
    movies: List[MovieResponse]
    # Реальный API возвращает count и pageCount, а не total/page/pageSize
    count: Optional[int] = None  # общее количество фильмов
    pageCount: Optional[int] = None  # количество страниц
    # Оставляем для совместимости со Swagger
    total: Optional[int] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None

    class Config:
        from_attributes = True
        extra = "ignore"


class CreateMovieRequest(BaseModel):
    """Модель запроса для создания фильма"""
    name: str
    imageUrl: str
    price: int
    description: str
    location: str
    published: bool
    genreId: int

    @validator('price')
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('price must be positive')
        return v

    @validator('location')
    def location_must_be_valid(cls, v):
        if v not in ['MSK', 'SPB']:
            raise ValueError('location must be MSK or SPB')
        return v


class UpdateMovieRequest(BaseModel):
    """Модель запроса для обновления фильма"""
    name: Optional[str] = None
    imageUrl: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    published: Optional[bool] = None
    genreId: Optional[int] = None