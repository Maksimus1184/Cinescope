"""
Pydantic модели для Movie API
Соответствуют реальному API
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator, Field


class Genre(BaseModel):
    """Модель жанра - API возвращает только name, id не всегда есть"""
    id: Optional[int] = None  # id может отсутствовать
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
    Адаптирована под реальный API
    """
    id: int
    name: str
    imageUrl: Optional[str] = None  # может быть null в БД
    price: int
    description: str
    location: str
    published: bool
    genreId: int
    createdAt: datetime
    rating: float  # убираем валидацию <=5, т.к. в БД есть значения >5
    reviews: List[Review] = []
    genre: Optional[Genre] = None  # genre может отсутствовать или быть без id

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


class MoviesListResponse(BaseModel):
    """
    Модель ответа для списка фильмов
    Адаптирована под реальный ответ API
    """
    movies: List[MovieResponse]
    # Делаем все поля Optional, так как API может не возвращать их
    total: Optional[int] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None
    pageCount: Optional[int] = None  # API возвращает pageCount вместо total?


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