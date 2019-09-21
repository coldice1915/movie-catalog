from database_setup import Base, User, Genre, Movie
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template
app = Flask(__name__)


engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/genre/<int:genre_id>/')
def genreMovie(genre_id):
    genre = session.query(Genre)
    movies = session.query(Movie)
    return render_template('movies.html', genre=genre, movies=movies)


@app.route('/genre/<int:genre_id>/new/')
def newMovie(genre_id):
    return "new movie page"


@app.route('/genre/<int:genre_id>/<int:movie_id>/edit/')
def editMovie(genre_id, movie_id):
    return "edit movie page"


@app.route('/genre/<int:genre_id>/<int:movie_id>/delete/')
def deleteMovie(genre_id, movie_id):
    return "delete movie page"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
