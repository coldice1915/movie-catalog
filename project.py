from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import Base, User, Genre, Film
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    # return "The current session state is %s" %login_session['state']


@app.route('/gconnect/', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
# Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
# Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
# Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
# Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

# Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

# Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
