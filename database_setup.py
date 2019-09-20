import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(base):
    __tablename__ = 'user'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)


class MovieGenre(base):
    __tablename__ = 'movie_genre'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('userid'))
    user = relationship(User)



class Movie(base):
    __tablename__ = 'movie'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)






engine = create_engine('sqlite:///')
Base.metadata.create_all(engine)
