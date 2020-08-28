#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Model.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
        return f'''
            <Venue {self.id} {self.name} {self.city} {self.state} {self.address}
            {self.phone} {self.image_link} {self.facebook_link} {self.website}
            {self.seeking_talent} {self.seeking_description}>
            '''

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artists', lazy=True)

    def __repr__(self):
        return f'''
            <Venue {self.id} {self.name} {self.city} {self.state}
            {self.phone} {self.image_link} {self.facebook_link} {self.website}>
            '''

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, default=datetime.utcnow)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

  def __repr__(self):
        return f'<Show {self.id} {self.start_time} {self.venue_id} {self.artist_id}>'

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  locations = Venue.query.distinct(Venue.city, Venue.state).all()

  data = []

  for location in locations:
    venues = []
    p_venues = Venue.query.filter(Venue.city == location.city, Venue.state == location.state).all()
    venues_data = {
      "city": location.city,
      "state": location.state
    }

    for p_venue in p_venues:
      num_upcoming_shows = Show.query.filter(Show.start_time >= datetime.now(), Show.venue_id == p_venue.id).count()
      venue = {
        "id": p_venue.id,
        "name": p_venue.name,
        "num_upcoming_shows": num_upcoming_shows
      }
      venues.append(venue)

    venues_data["venues"] = venues
    data.append(venues_data)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')

  data = []

  # Search term in venue name
  venues = (db.session
        .query(Venue.id, Venue.name)
        .filter(Venue.name.ilike("%{}%".format(search_term)))
        .all())

  count = len(venues)

  # Search term in artist name and display show venue
  venues_artist = (db.session
          .query(Venue.id, Venue.name)
          .join(Show, Show.venue_id == Venue.id)
          .join(Artist, Show.artist_id == Artist.id)
          .filter(Artist.name.ilike('%{}%'.format(search_term)))
          .all())

  count = count + len(venues_artist)

  venues_artist = list(dict.fromkeys(venues_artist))

  if len(venues) == 0:
    data = venues_artist
  elif len(venues_artist) == 0:
    data = venues
  else:
    for venue in venues_artist:
      if venue not in venues:
        venues.append(venue)
    
    data = venues

  response={
    "count": count,
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  data = {}

  venues = Venue.query.filter(Venue.id == venue_id).all()

  if len(venues) == 0:
    flash('No data with Venue id = ' + venue_id + ' could be found!')
    return redirect(url_for('venues'))

  past_shows = []

  temp_past_shows = (db.session
          .query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
          .join(Venue, Venue.id == Show.venue_id)
          .join(Artist, Artist.id == Show.artist_id)
          .filter(Show.start_time < db.func.current_timestamp(), Venue.id == venue_id)
          .all())

  past_shows_count = len(temp_past_shows)

  if past_shows_count > 0:
    for past_show in temp_past_shows:
      past_shows.append({
          "artist_id": past_show[0],
          "artist_name": past_show[1],
          "artist_image_link": past_show[2],
          "start_time": str(past_show[3])
      })

  upcoming_shows = []

  temp_upcoming_shows = (db.session
          .query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
          .join(Venue, Venue.id == Show.venue_id)
          .join(Artist, Artist.id == Show.artist_id)
          .filter(Show.start_time >= db.func.current_timestamp(), Venue.id == venue_id)
          .all())
    
  upcoming_shows_count = len(temp_upcoming_shows)

  if upcoming_shows_count > 0:
    for upcoming_show in temp_upcoming_shows:
      upcoming_shows.append({
          "artist_id": upcoming_show[0],
          "artist_name": upcoming_show[1],
          "artist_image_link": upcoming_show[2],
          "start_time": str(upcoming_show[3])
      })

  data['id'] = venue_id
  data['name'] = venues[0].name
  data['genres'] = venues[0].genres.split(',')
  data['address'] = venues[0].address
  data['city'] = venues[0].city
  data['state'] = venues[0].state
  data['phone'] = venues[0].phone
  data['website'] = venues[0].website
  data['facebook_link'] = venues[0].facebook_link
  data['seeking_talent'] = venues[0].seeking_talent
  data['seeking_description'] = venues[0].seeking_description
  data['image_link'] =  venues[0].image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  venue = Venue(
    name = request.form.get('name', ''),
    city = request.form.get('city', ''),
    state = request.form.get('state', ''),
    address = request.form.get('address', ''),
    phone = request.form.get('phone', ''),
    genres = ','.join(request.form.getlist('genres')),
    image_link = request.form.get('image_link', ''),
    facebook_link = request.form.get('facebook_link', ''),
    website = request.form.get('website', ''),
    seeking_talent = request.form.get('seeking_talent', False),
    seeking_description = request.form.get('seeking_description', '')
  )

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name', '') + ' was successfully added!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form.get('name', '') + ' could not be added!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_id + ' was successfully deleted!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_id + ' fail to be deleted!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = []

  artists = Artist.query.all()

  for artist in artists:
    temp = {}
    temp['id'] = artist.id
    temp['name'] = artist.name
    data.append(temp)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  
  artists = (db.session
          .query(Artist.id, Artist.name)
          .filter(Artist.name.ilike('%{}%'.format(search_term)))
          .all())

  count = len(artists)

  data = []

  for artist in artists:
    temp = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(temp)

  response = {
    "count": count,
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
  data = {}

  artists = Artist.query.filter(Artist.id == artist_id).all()

  if len(artists) == 0:
    flash('No data with Artist id = ' + artist_id + ' could be found!')
    return redirect(url_for('artists'))

  past_shows = []

  temp_past_shows = (db.session
          .query(Venue.id, Venue.name, Venue.image_link, Show.start_time)
          .join(Artist, Artist.id == Show.artist_id)
          .join(Venue, Venue.id == Show.venue_id)
          .filter(Show.start_time < db.func.current_timestamp(), Artist.id == artist_id)
          .all())

  past_shows_count = len(temp_past_shows)

  if past_shows_count > 0:
    for past_show in temp_past_shows:
      past_shows.append({
          "venue_id": past_show[0],
          "venue_name": past_show[1],
          "venue_image_link": past_show[2],
          "start_time": str(past_show[3])
      })

  upcoming_shows = []

  temp_upcoming_shows = (db.session
          .query(Venue.id, Venue.name, Venue.image_link, Show.start_time)
          .join(Artist, Artist.id == Show.artist_id)
          .join(Venue, Venue.id == Show.venue_id)
          .filter(Show.start_time >= db.func.current_timestamp(), Artist.id == artist_id)
          .all())
    
  upcoming_shows_count = len(temp_upcoming_shows)

  if upcoming_shows_count > 0:
    for upcoming_show in temp_upcoming_shows:
      upcoming_shows.append({
          "venue_id": upcoming_show[0],
          "venue_name": upcoming_show[1],
          "venue_image_link": upcoming_show[2],
          "start_time": str(upcoming_show[3])
      })

  data['id'] = artist_id
  data['name'] = artists[0].name
  data['genres'] = artists[0].genres.split(',')
  data['city'] = artists[0].city
  data['state'] = artists[0].state
  data['phone'] = artists[0].phone
  data['website'] = artists[0].website
  data['facebook_link'] = artists[0].facebook_link
  data['seeking_venue'] = artists[0].seeking_venue
  data['seeking_description'] = artists[0].seeking_description
  data['image_link'] =  artists[0].image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>

  artist = {}

  artists = Artist.query.filter(Artist.id == artist_id).all()

  if len(artists) == 0:
    flash('No data with Artist id = ' + artist_id + ' could be found!')
    return redirect(url_for('artists'))

  artist['id'] = artist_id
  artist['name'] = artists[0].name
  artist['genres'] = artists[0].genres.split(',')
  artist['city'] = artists[0].city
  artist['state'] = artists[0].state
  artist['phone'] = artists[0].phone
  artist['website'] = artists[0].website
  artist['facebook_link'] = artists[0].facebook_link
  artist['seeking_venue'] = artists[0].seeking_venue
  artist['seeking_description'] = artists[0].seeking_description
  artist['image_link'] =  artists[0].image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    artist = Artist(
      name = request.form.get('name', ''),
      city = request.form.get('city', ''),
      state = request.form.get('state', ''),
      phone = request.form.get('phone', ''),
      genres = ','.join(request.form.getlist('genres')),
      image_link = request.form.get('image_link', ''),
      facebook_link = request.form.get('facebook_link', ''),
      website = request.form.get('website', ''),
      seeking_venue = request.form.get('seeking_venue', False),
      seeking_description = request.form.get('seeking_description', '')
    )

    try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form.get('name', '') + ' was successfully added!')
    except:
      print(sys.exc_info)
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form.get('name', '') + ' could not be added!')
    finally:
      db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>

  venue = {}

  venues = Venue.query.filter(Venue.id == venue_id).all()

  if len(venues) == 0:
    flash('No data with Venue id = ' + venue_id + ' could be found!')
    return redirect(url_for('venues'))

  venue['id'] = venue_id
  venue['name'] = venues[0].name
  venue['genres'] = venues[0].genres.split(',')
  venue['address'] = venues[0].address
  venue['city'] = venues[0].city
  venue['state'] = venues[0].state
  venue['phone'] = venues[0].phone
  venue['website'] = venues[0].website
  venue['facebook_link'] = venues[0].facebook_link
  venue['seeking_talent'] = venues[0].seeking_talent
  venue['seeking_description'] = venues[0].seeking_description
  venue['image_link'] =  venues[0].image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue(
    name = request.form.get('name', ''),
    address = request.form.get('address', ''),
    city = request.form.get('city', ''),
    state = request.form.get('state', ''),
    phone = request.form.get('phone', ''),
    genres = ','.join(request.form.getlist('genres')),
    image_link = request.form.get('image_link', ''),
    facebook_link = request.form.get('facebook_link', ''),
    website = request.form.get('website', ''),
    seeking_talent = request.form.get('seeking_talent', False),
    seeking_description = request.form.get('seeking_description', '')
  )

  try:
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name', '') + ' was successfully added!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form.get('name', '') + ' could not be added!')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  artist = Artist(
    name = request.form.get('name', ''),
    city = request.form.get('city', ''),
    state = request.form.get('state', ''),
    address = request.form.get('address', ''),
    phone = request.form.get('phone', ''),
    genres = ','.join(request.form.getlist('genres')),
    image_link = request.form.get('image_link', ''),
    facebook_link = request.form.get('facebook_link', ''),
    website = request.form.get('website', '')
  )

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form.get('name', '') + ' was successfully added!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form.get('name', '') + ' could not be added!')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = (Show
      .query(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time)
      .join(Venue, Show.venue_id == Venue.id)
      .join(Artist, Show.artist_id == Artist.id)
      .filter()
      .all())

  data = []
  
  for show in shows:
    temp = {}
    temp['venue_id'] = show['Venue.id']
    temp['venue_name'] = show['Venue.name']
    temp['artist_id'] = show['Artist.id'] 
    temp['artist_name'] = show['Artist.name']
    temp['artist_image_link'] = show['Artist.image_link']
    temp['start_time'] = show['start_time']

    data.append(temp)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  show = Show (
    venus_id = request.form.get('venue_id', ''),
    artist_id = request.form.get('artist_id', ''),
    start_time = request.form.get('start_time', datetime.utcnow())
  )

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  try:
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Show could not be added!')
  finally:
    db.session.close()

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
if __name__ == '__main__':
  app = create_app()
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
'''
