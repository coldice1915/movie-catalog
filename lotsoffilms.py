from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Genre, Film


engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Action Films
actionGenre = Genre(name="Action")

session.add(actionGenre)
session.commit()

film1 = Film(name="Avengers", summary="Heroes coming together from different movies, the good guys with superpowers band together to fight the bad guy.", rating="8.0", whatType="Movie", link="https://www.youtube.com/watch?v=eOrNdBpGMv8/", genre=actionGenre)

session.add(film1)
session.commit()


# Comedy Films
comedyGenre = Genre(name="Comedy")

session.add(comedyGenre)
session.commit()

film2 = Film(name="The Big Lebowski", summary="Jeff 'The Dude' Lebowski, mistaken for a millionaire of the same name, seeks restitution for his ruined rug and enlists his bowling buddies to help get it.", rating="8.5", whatType="Movie", link="", genre=comedyGenre)

session.add(film2)
session.commit()