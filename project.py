from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import Base, User, Genre, Film
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Making API Endpoint (GET Request)
@app.route('/genre/JSON/')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[g.serialize for g in genres])


@app.route('/genre/<int:genre_id>/film/JSON/')
def genreFilmJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    films = session.query(Film).filter_by(genre_id=genre_id).all()
    return jsonify(Films=[f.serialize for f in films])


@app.route('/genre/<int:genre_id>/film/<int:film_id>/JSON/')
def filmJSON(genre_id, film_id):
    film = session.query(Film).filter_by(id=film_id).one()
    return jsonify(film=film.serialize)


# Show all genres
@app.route('/')
@app.route('/genre/')
def showGenres():
    genres = session.query(Genre).all()
    return render_template('genres.html', genres=genres)
    # return "This page will show all my restaurants"


# Create a new genre
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if request.method == 'POST':
        newGenre = Genre(name=request.form['name'])
        session.add(newGenre)
        session.commit()
        flash("New genre added!")
        return redirect(url_for('showGenres'))
    else:
        return render_template('newGenre.html')
    # return "This page will be for making a new genre"


# Edit a genre
@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    editedGenre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
            flash("Genre edited!")
            return redirect(url_for('showGenres'))
    else:
        return render_template('editGenre.html', genre=editedGenre)
    # return 'This page will be for editing genre %s' % genre_id


# Delete a genre
@app.route('/genre/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    genreToDelete = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        session.delete(genreToDelete)
        session.commit()
        flash("Genre deleted!")
        return redirect(url_for('showGenres', genre_id=genre_id))
    else:
        return render_template('deleteGenre.html', genre=genreToDelete)
    # return 'This page will be for deleting genre %s' % genre_id


# Show films
@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/film/')
def showFilm(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    films = session.query(Film).filter_by(genre_id=genre_id).all()
    return render_template('film.html', films=films, genre=genre)
    # return 'This page has the film for genre %s' % genre_id


# Add a new film
@app.route('/genre/<int:genre_id>/film/new/', methods=['GET', 'POST'])
def addFilm(genre_id):
    if request.method == 'POST':
        addNewFilm = Film(name=request.form['name'], summary=request.form['summary'], rating=request.form['rating'],
                          whatType=request.form['whatType'], link=request.form['link'], genre_id=genre_id)
        session.add(addNewFilm)
        session.commit()
        flash("New film added!")
        return redirect(url_for('showGenres', genre_id=genre_id))
    else:
        return render_template('addFilm.html', genre_id=genre_id)


# Edit a film
@app.route('/genre/<int:genre_id>/film/<int:film_id>/edit', methods=['GET', 'POST'])
def editFilm(genre_id, film_id):
    editedFilm = session.query(Film).filter_by(id=film_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedFilm.name = request.form['name']
        if request.form['summary']:
            editedFilm.summary = request.form['summary']
        if request.form['rating']:
            editedFilm.rating = request.form['rating']
        if request.form['whatType']:
            editedFilm.whatType = request.form['whatType']
        if request.form['link']:
            editedFilm.link = request.form['link']
        session.add(editedFilm)
        session.commit()
        flash("Film edited!")
        return redirect(url_for('showFilm', genre_id=genre_id))
    else:
        return render_template('editFilm.html', genre_id=genre_id, film_id=film_id, film=editedFilm)
    # return 'This page is for editing film %s' % film_id


# Delete a film
@app.route('/genre/<int:genre_id>/film/<int:film_id>/delete', methods=['GET', 'POST'])
def deleteFilm(genre_id, film_id):
    filmToDelete = session.query(Film).filter_by(id=film_id).one()
    if request.method == 'POST':
        session.delete(filmToDelete)
        session.commit()
        flash("Film deleted!")
        return redirect(url_for('showFilm', genre_id=genre_id))
    else:
        return render_template('deleteFilm.html', film=filmToDelete)
    # return "This page is for deleting menu item %s" % menu_id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
