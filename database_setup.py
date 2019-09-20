import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)


class MovieGenre(Base):
    __tablename__ = 'movieGenre'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Movie(Base):
    __tablename__ = 'movie'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    summary = Column(String(250))
    rating = Column(String(80))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    movieGenre_id = Column(Integer, ForeignKey('movieGenre.id'))
    movieGenre = relationship(MovieGenre)


engine = create_engine('sqlite:///moviecatalog.db')


Base.metadata.create_all(engine)
