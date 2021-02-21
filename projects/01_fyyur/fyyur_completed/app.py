#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from sqlalchemy import update
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models. - models.py
#----------------------------------------------------------------------------#
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

def date_check(start_time):
    if dateutil.parser.parse(start_time) >= datetime.now():
        upcoming = True
    else:
        upcoming = False
    return upcoming

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    locations = Venue.query.distinct(Venue.city, Venue.state)
    for location in locations:
        venue_list = Venue.query.filter_by(city=location.city, state=location.state)
        list_item={
            "city": location.city,
            "state": location.state,
            "venues": venue_list
        }
        data.append(list_item)

    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form['search_term']
    search_result = Venue.query.filter(
        Venue.name.ilike("%" + format(search_term) + "%")
    ).order_by(Venue.name).all()

    result = {
        "count": len(list(search_result)),
        "data": [{
            "id": venue.id,
            "name": venue.name
        } for venue in search_result]
    }

    return render_template('pages/search_venues.html', results=result, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)

    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id
    ).order_by(Show.start_time).all()

    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id
    ).order_by(Show.start_time).all()

    data = {
        "id" : venue.id,
        "name" : venue.name,
        "image_link" : venue.image_link,
        "address" : venue.address,
        "city" : venue.city,
        "state" : venue.state,
        "genres" : venue.genres,
        "phone" : venue.phone,
        "facebook_link" : venue.facebook_link,
        "website" : venue.website,
        "seeking_talent" : venue.seeking_talent,
        "seeking_description" : venue.seeking_description,
        "past_shows": [{
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
        } for artist, show in past_shows],
        "past_shows_count" : len(past_shows),
        "upcoming_shows": [{
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
        } for artist, show in upcoming_shows],
        "upcoming_shows_count" : len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    error = False
    try:
        new_venue = Venue(
            name = request.form['name'],
            city = request.form['city'],
            state = request.form['state'],
            address = request.form['address'],
            phone = request.form['phone'],
            facebook_link = request.form['facebook_link'],
            genres = request.form.getlist('genres')
        )
        db.session.add(new_venue)
        db.session.commit()
        new_venue_id = new_venue.id
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
        flash('An error occurred. Venue ' + name + ' could not be listed.')
    else:
        return redirect(url_for('show_venue', venue_id=new_venue_id))

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
    else:
        return render_template('pages/home.html')
    return None

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    venue = Venue.query.get_or_404(venue_id)
    try:
        if request.form['name']:
            venue.name = request.form['name']
        if request.form['city']:
            venue.city = request.form['city']
        if request.form['state']:
            venue.state = request.form['state']
        if request.form['address']:
            venue.address = request.form['address']
        if request.form['phone']:
            venue.phone = request.form['phone']
        if request.form['facebook_link']:
            venue.facebook_link = request.form['facebook_link']
        if request.form['genres']:
            venue.genres = request.form.getlist('genres')
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
        flash('An error occurred. Venue could not be updated.')
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

    error = False
    try:
        data = Artist.query.order_by(Artist.name).all()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form['search_term']
    search_result = Artist.query.filter(
        Artist.name.like("%" + format(search_term) + "%")
    ).order_by(Artist.name).all()

    result = {
        "count": len(list(search_result)),
        "data": [{
                "id": artist.id,
                "name": artist.name
            } for artist in search_result]
    }

    return render_template('pages/search_artists.html', results=result, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)

    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id
    ).order_by(Show.start_time).all()

    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id
    ).order_by(Show.start_time).all()

    data = {
        "id" : artist.id,
        "name" : artist.name,
        "image_link" : artist.image_link,
        "genres" : artist.genres,
        "city" : artist.city,
        "state" : artist.state,
        "phone" : artist.phone,
        "website" : artist.website,
        "facebook_link" : artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": [{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
        } for venue, show in past_shows],
        "past_shows_count" : len(past_shows),
        "upcoming_shows": [{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
        } for venue, show in upcoming_shows],
        "upcoming_shows_count" : len(upcoming_shows)
    }
    print(data)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    artist = Artist.query.get_or_404(artist_id)
    try:
        if request.form['name']:
            artist.name = request.form['name']
        if request.form['city']:
            artist.city = request.form['city']
        if request.form['state']:
            artist.state = request.form['state']
        if request.form['phone']:
            artist.phone = request.form['phone']
        if request.form['facebook_link']:
            artist.facebook_link = request.form['facebook_link']
        if request.form['genres']:
            artist.genres = request.form.getlist('genres')
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
        flash('An error occurred. Artist could not be updated.')
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False

    try:
        new_artist = Artist(
            name = request.form['name'],
            city = request.form['city'],
            state = request.form['state'],
            phone = request.form['phone'],
            image_link = request.form['image_link'],
            facebook_link = request.form['facebook_link'],
            genres = request.form.getlist('genres')
        )
        db.session.add(new_artist)
        db.session.commit()
        new_artist_id = new_artist.id
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

        return redirect(url_for('show_artist', artist_id=new_artist_id))
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.order_by(Show.start_time).all()
  list = []
  list_item = []
  for show in shows:
      list_item={
        "venue_id": show.venue_id,
        "venue_name": Venue.query.get_or_404(show.venue_id).name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get_or_404(show.artist_id).name,
        "artist_image_link": Artist.query.get_or_404(show.artist_id).image_link,
        "start_time": show.start_time
      }
      list.append(list_item)
  return render_template('pages/shows.html', shows=list)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    try:
        new_show = Show(
            artist_id = artist_id,
            venue_id = venue_id,
            start_time = start_time
        )
        venue = Venue.query.get_or_404(venue_id)
        artist = Artist.query.get_or_404(artist_id)

        db.session.add(new_show)
        db.session.commit()
    except():
        dump(request)
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)

        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

        return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5000, debug=True)
