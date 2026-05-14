"""
Pydantic models for API testing
"""
from models.movie import (
    MovieResponse,
    MoviesListResponse,
    CreateMovieRequest,
    UpdateMovieRequest,
    Genre,
    Review
)
from models.user import (
    UserResponse,
    LoginRequest,
    LoginResponse
)

__all__ = [
    # Movie models
    'MovieResponse',
    'MoviesListResponse',
    'CreateMovieRequest',
    'UpdateMovieRequest',
    'Genre',
    'Review',
    # User models
    'UserResponse',
    'LoginRequest',
    'LoginResponse'
]