from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer
from sqlalchemy.orm import declarative_base
from typing import Dict, Any

Base = declarative_base()


class MovieDBModel(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)  # serial4 в БД -> int в Python
    name = Column(String)  # text в БД
    description = Column(String)  # text в БД
    price = Column(Integer)  # int4 в БД (из вашего описания price int4)
    image_url = Column(String)  # text в БД
    location = Column(String)  # text в БД
    published = Column(Boolean)  # bool в БД
    created_at = Column(DateTime)  # timestamp в БД
    rating = Column(Float)  # float8 в БД
    genre_id = Column(Integer)  # int4 в БД

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'created_at': self.created_at,
            'rating': self.rating,
            'genre_id': self.genre_id
        }

    def __repr__(self):
        return f"<Movie(id='{self.id}', name='{self.name}', price={self.price})>"

