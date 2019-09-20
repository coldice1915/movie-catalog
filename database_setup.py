import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class MovieGenre(Base):
    __tablename__ = 'movie_genre'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Movie(Base):
    __tablename__ = 'movie'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    summary = Column(String(250))
    rating = Column(String(80))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    movie_genre_id = Column(Integer, ForeignKey('movie_genre.id'))
    movie_genre = relationship(MovieGenre)


engine = create_engine('sqlite:///moviecatalog.db')


Base.metadata.create_all(engine)
