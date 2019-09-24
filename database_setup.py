import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)


class Genre(Base):
    __tablename__ = 'genre'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Film(Base):
    __tablename__ = 'film'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    summary = Column(String(250))
    rating = Column(String(4))
    whatType = Column(String(250))
    link = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'summary': self.summary,
            'rating': self.rating,
            'whatType': self.whatType,
            'link': self.link
        }


engine = create_engine('sqlite:///moviecatalog.db')


Base.metadata.create_all(engine)
