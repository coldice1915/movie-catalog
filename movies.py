from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, MovieGenre, Movie


engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

actionGenre = MovieGenre(name="Action")

session.add(actionGenre)
session.commit()
session.query(MovieGenre).all()

avengers = Movie(name="The Avengers",
                 summary="Coming together from separate movies, good guys with superpowers band together to fight the bad guy.", rating="8.0", movie_genre=actionGenre)

session.add(avengers)
session.commit()
session.query(Movie).all()
