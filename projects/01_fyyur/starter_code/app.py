#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ast import Not
import json
from select import select
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from datetime import datetime
from flask_migrate import Migrate
import sys
from os import abort
from sqlalchemy import select

from flask_wtf.csrf import CSRFProtect


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

app.config['WTF_CSRF_SECRET_KEY'] = 'your_csrf_secret_key'
app.config['SECRET_KEY'] = 'your_secret_key'

csrf = CSRFProtect(app)
csrf.init_app(app)



# TODO: connect to a local postgresql database
## I have connected to the database on config.py file

from models import db, Artist, Venue, Show

migrate = Migrate(app, db)

db.init_app(app)











#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

###################################################################################################################
###################################################################################################################
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  #query diffrent existing cities and states:
  
  ## Done 
  city_state_rows = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()

  
  data = []
  
  for city_state in city_state_rows:
    city_state_dict = {}
    city_state_dict["city"] = city_state[0]
    city_state_dict["state"] = city_state[1]
   
    #query additional venue columns
    venues_id_name_rows = Venue.query.with_entities(Venue.id, Venue.name).filter_by(city=city_state[0], state=city_state[1]).all()
    
    venue_list = []   
    
    for venue_id_name in venues_id_name_rows:
      venue_dict = {}
      venue_dict["id"] = venue_id_name[0]
      venue_dict["name"] = venue_id_name[1] 

## This section is to extract date_time from db, to format it, & to compare
      date_times = Show.query.with_entities(Show.datetime).filter_by(venue_id = venue_dict["id"]).all()
      num_upcoming_shows = 0
      
      for date_time_row in date_times:
        
        date_time_db = date_time_row._mapping['datetime']
        date_time_now = datetime.today()
        
        if date_time_db > date_time_now:
          num_upcoming_shows += 1
  ################      
      venue_dict["num_upcoming_shows"] = num_upcoming_shows

      venue_list.append(venue_dict)
      
    city_state_dict["venues"] = venue_list
    data.append(city_state_dict)
    
  return render_template('pages/venues.html', areas=data)
###################################################################################################################
###################################################################################################################






###################################################################################################################
###################################################################################################################
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  ##Done
  
  
  # get the search term from the search bar
  to_search = request.form["search_term"]
  
  # count results from the database
  count = Venue.query.filter(Venue.name.ilike('%'+to_search+'%')).count()
  
  # get the query from the database
  venue_query = Venue.query.with_entities(Venue.id ,Venue.name).filter(Venue.name.ilike('%'+to_search+'%')).all()
  
  # Response dictionary
  response = {}
  
  response["count"] = count
  
  ## data list to fill with selected venues 
  data = []
  
  
  for venue in venue_query:
    
    venue_dict = {}
    venue_dict["id"] = venue [0]    
    venue_dict["name"] = venue [1]
    
## This section is to extract date_time from db, to format it, & to compare
    date_times = Show.query.with_entities(Show.datetime).filter_by(venue_id = venue_dict["id"]).all()
    num_upcoming_shows = 0
    
    for date_time_row in date_times:
      
      date_time_db = date_time_row._mapping['datetime']
      date_time_now = datetime.today()
      
      if date_time_db > date_time_now:
        num_upcoming_shows += 1
################      
    venue_dict["num_upcoming_shows"] = num_upcoming_shows
    
    data.append(venue_dict)
  
  response["data"] = data
    

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

###################################################################################################################
###################################################################################################################





###################################################################################################################
###################################################################################################################
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  ## Done
  
  data = {}
  
  venue = Venue.query.get(venue_id)
  
  data["id"] = venue_id
  data["name"] = venue.name
  
  ### To Get data["genres"]  ↓↓↓↓
  ## venue.genres == '{Alternative,Blues,Classical,Country}' and is of type str
  ## venue.genres[1:-1] == 'Alternative,Blues,Classical,Country' and is of type str
  ## venue.genres[1:-1].split(',') == ['Alternative', 'Blues', 'Classical', 'Country'] and is of type list
  data["genres"] = venue.genres[1:-1].split(',')
  
  data["address"] = venue.address
  data["city"] = venue.city
  data["state"] = venue.state
  data["phone"] = venue.phone
  data["website"] = venue.website_link
  data["facebook_link"] = venue.facebook_link  
  data["seeking_talent"] = (venue.seeking == 'true')
  data["seeking_description"] = venue.detail_seeking
  data["image_link"] = venue.image_link  
 
 
  
  #### get past_shows_query  with Join
  data["past_shows"] = []
  past_shows_count = 0
  
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.datetime<datetime.now()).all() 
  
  for show in past_shows_query:
    past_shows_count += 1
    artist_id = show.artist_id
    artist = Artist.query.get(artist_id)

    show_dict = {}
    show_dict["artist_id"] = artist_id
    
    show_dict["artist_name"] = artist.name
    show_dict["artist_image_link"] = artist.image_link
    start_time = show.datetime
    show_dict["start_time"] = format_datetime(str(start_time))
    
    data["past_shows"].append(show_dict)
    
  data["past_shows_count"] = past_shows_count
  


  #### get upcoming_shows  with Join
  upcoming_shows_count = 0
  data["upcoming_shows"] = []
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.datetime>datetime.now()).all() 
  
  for show in upcoming_shows_query:
    upcoming_shows_count += 1

    artist_id = show.artist_id
    artist = Artist.query.get(artist_id)

    show_dict = {}
    show_dict["artist_id"] = artist_id
    show_dict["artist_name"] = artist.name
    show_dict["artist_image_link"] = artist.image_link
    start_time = show.datetime
    show_dict["start_time"] = format_datetime(str(start_time))
    
    data["upcoming_shows"].append(show_dict)
    
  data["upcoming_shows_count"] = upcoming_shows_count
  

  
############ My previous method to  get Shows --- Not used anymore
# shows = Show.query.filter_by(venue_id = venue_id).all()
#
# past_shows_count = 0
# upcoming_shows_count = 0
# for show in shows:
#   artist_id = show.artist_id
#   artist = Artist.query.get(artist_id)
#
#   show_dict = {}
#   show_dict["artist_id"] = artist_id
#   show_dict["artist_name"] = artist.name
#   show_dict["artist_image_link"] = artist.image_link
#   start_time = show.datetime
#   show_dict["start_time"] = format_datetime(str(start_time))
#  
#   if start_time > datetime.today():
#     upcoming_shows_count += 1
#     data["upcoming_shows"].append(show_dict)
#   else:
#     past_shows_count += 1
#     data["past_shows"].append(show_dict)
# 
#
# data["past_shows_count"] = past_shows_count
# data["upcoming_shows_count"] = upcoming_shows_count
#
###################################################################### 
 # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  return render_template('pages/show_venue.html', venue=data)

###################################################################################################################
###################################################################################################################







#  Create Venue
#  ----------------------------------------------------------------

###################################################################################################################
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
###################################################################################################################




###################################################################################################################
###################################################################################################################
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  form = VenueForm()
 
  #Done
  error = False
  if form.validate_on_submit():
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']      
        phone = request.form['phone']      
        image_link = request.form['image_link'] 
        facebook_link = request.form['facebook_link']
  
        website_link = request.form['website_link']   

        try:
          if request.form['seeking_talent'] == 'y':
            seeking = True
        except:
          seeking = False
        
        detail_seeking = request.form['seeking_description']  
        genres = request.form.to_dict(flat=False)['genres']
      
        venue = Venue(name = name,
                      city = city,
                      state = state,
                      address = address,
                      phone = phone,
                      image_link = image_link,
                      facebook_link = facebook_link,
                      website_link = website_link,
                      seeking = seeking,
                      detail_seeking = detail_seeking,
                      genres = genres
                      )

        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
          db.session.close()
      
    if not error :
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully listed!')

        
    
    else:
      
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + name + ' could not be listed.')
    
    return render_template('pages/home.html')
  
  
  else:
    for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
  
  return render_template('forms/new_venue.html', form=form)
      

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
###################################################################################################################
###################################################################################################################  





@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  
  try:
      venue = Venue.query.get(venue_id)
      
      for artist in venue.artists:
          db.session.delete(artist)

      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  
  
  return render_template('pages/home.html')






#  Artists
#  ----------------------------------------------------------------


###################################################################################################################
###################################################################################################################
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # Done:
  
  artists_ids_rows = Artist.query.with_entities(Artist.id).all()

  data = []
  
  for artist_id_row in artists_ids_rows:
    artist_dict = {} 
    
    # Extract artist id
    artist_id_str = str(artist_id_row)   
    artist_id =  artist_id_str[1:-2]
    
    # Extract Artist Name
    artist_name_row = Artist.query.with_entities(Artist.name).filter_by(id=artist_id).first()
    artist_name_str = str(artist_name_row)
    artist_name = artist_name_str[2:-3]   
    
    
    # add the artist to the dictionnary
    artist_dict["id"] = artist_id
    artist_dict["name"] = artist_name
    
    #Add the dictionnary to the data list
    data.append(artist_dict)
    
    
  return render_template('pages/artists.html', artists=data)
###################################################################################################################
###################################################################################################################






###################################################################################################################
###################################################################################################################
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  ##Done 
  
  # get the search term from the search bar
  to_search = request.form["search_term"]
  
  # count results from the database
  count = Artist.query.filter(Artist.name.ilike('%'+to_search+'%')).count()
  
  # get the query from the database
  artist_query = Artist.query.with_entities(Artist.id ,Artist.name).filter(Artist.name.ilike('%'+to_search+'%')).all()
   
  # Response dictionary
  response = {}
  
  response["count"] = count
  
  ## data list to fill with selected artists 
  data = []
  
  for artist in artist_query:
    
    artist_dict = {}
    artist_dict["id"] = artist [0]    
    artist_dict["name"] = artist [1]
  
## This section is to extract date_time from db, to format it, & to compare
    date_times = Show.query.with_entities(Show.datetime).filter_by(artist_id = artist_dict["id"]).all()
    num_upcoming_shows = 0
    
    for date_time_row in date_times:
      
      date_time_db = date_time_row._mapping['datetime']
      date_time_now = datetime.today()
      
      if date_time_db > date_time_now:
        num_upcoming_shows += 1
################ 
    artist_dict["num_upcoming_shows"] = num_upcoming_shows
    
    data.append(artist_dict)
  
  response["data"] = data
  

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
###################################################################################################################
###################################################################################################################





###################################################################################################################
###################################################################################################################
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  ## Done
  
  data = {}
  
  artist = Artist.query.get(artist_id)
  
  data["id"] = artist_id
  data["name"] = artist.name

  ### To Get data["genres"]  ↓↓↓↓
  ## artist.genres == '{Alternative,Blues,Classical,Country}' and is of type str
  ## artist.genres[1:-1] == 'Alternative,Blues,Classical,Country' and is of type str
  ## artist.genres[1:-1].split(',') == ['Alternative', 'Blues', 'Classical', 'Country'] and is of type list
  data["genres"] = artist.genres[1:-1].split(',')
  
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website"] = artist.website_link
  data["facebook_link"] = artist.facebook_link  
  data["seeking_venue"] = (artist.seeking == 'true')
  
  print('######################## Seeking', data["seeking_venue"] , type(data["seeking_venue"]) )
  
  data["seeking_description"] = artist.detail_seeking
  data["image_link"] = artist.image_link
  

  

  #### get past_shows_query  with Join
  data["past_shows"] = []
  past_shows_count = 0
  
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.datetime<datetime.now()).all() 
  
  for show in past_shows_query:
    past_shows_count += 1
    venue_id = show.venue_id
    venue = Venue.query.get(venue_id)

    show_dict = {}
    show_dict["venue_id"] = venue_id
    
    show_dict["venue_name"] = venue.name
    show_dict["venue_image_link"] = venue.image_link
    start_time = show.datetime
    show_dict["start_time"] = format_datetime(str(start_time))
    
    data["past_shows"].append(show_dict)
    
  data["past_shows_count"] = past_shows_count
  


  #### get upcoming_shows  with Join
  upcoming_shows_count = 0
  data["upcoming_shows"] = []
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.datetime>datetime.now()).all() 
  
  for show in upcoming_shows_query:
    upcoming_shows_count += 1

    venue_id = show.venue_id
    venue = Venue.query.get(venue_id)

    show_dict = {}
    show_dict["venue_id"] = venue_id
    show_dict["venue_name"] = venue.name
    show_dict["artist_image_link"] = venue.image_link
    start_time = show.datetime
    show_dict["start_time"] = format_datetime(str(start_time))
    
    data["upcoming_shows"].append(show_dict)
    
  data["upcoming_shows_count"] = upcoming_shows_count

  

  
############ My previous method to  get Shows --- Not used anymore
# shows = Show.query.filter_by(artist_id = artist_id).all()
#
# past_shows_count = 0
# upcoming_shows_count = 0
#
# for show in shows:
#   venue_id = show.venue_id
#   venue = Venue.query.get(venue_id)
#
#   show_dict = {}
#   show_dict["venue_id"] = venue_id
#   show_dict["venue_name"] = venue.name
#   show_dict["venue_image_link"] = venue.image_link
#   start_time = show.datetime
#   show_dict["start_time"] = format_datetime(str(start_time))
# 
#   if start_time > datetime.today():
#     upcoming_shows_count += 1
#     data["upcoming_shows"].append(show_dict)
#   else:
#     past_shows_count += 1
#     data["past_shows"].append(show_dict)
#  
#
# data["past_shows_count"] = past_shows_count
# data["upcoming_shows_count"] = upcoming_shows_count
############################################################
  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)
###################################################################################################################
###################################################################################################################






#  Update
#  ----------------------------------------------------------------



###################################################################################################################
###################################################################################################################
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>

  ## Done
  
  artist_data = Artist.query.get(artist_id)
  artist = {}
  artist["id"] = artist_id
  artist["name"] = artist_data.name
  artist["genres"] = artist_data.genres[1:-1].split(',')
  artist["city"] = artist_data.city
  artist["state"] = artist_data.state
  artist["phone"] = artist_data.phone
  artist["website"] = artist_data.website_link
  artist["facebook_link"] = artist_data.facebook_link
  artist["seeking_venue"] = ( artist_data.seeking == 'true')
  artist["seeking_description"] = artist_data.detail_seeking
  artist["image_link"] = artist_data.image_link
  
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)
###################################################################################################################
###################################################################################################################





###################################################################################################################
###################################################################################################################
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  ## Done
  form = ArtistForm()

  error = False
  if form.validate_on_submit():
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']     
        phone = request.form['phone']      
        image_link = request.form['image_link'] 
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']
        try:
          if request.form['seeking_venue'] == 'y':
            seeking = True
        except:
          seeking = False
          
        detail_seeking = request.form['seeking_description']  

        ## I have to convert the form into a dictionary in order to extract all genre values
        genres = request.form.to_dict(flat=False)['genres']
    
        artist = Artist.query.get(artist_id)
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.image_link = image_link
        artist.facebook_link = facebook_link
        artist.website_link = website_link
        artist.seeking = seeking
        artist.detail_seeking = detail_seeking
        artist.genres = genres
                      

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
          db.session.close()
      
    if not error :
        # on successful db insert, flash success
        flash('Artist ' + name + ' was successfully updated!')      
    
    else:
      
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + name + ' could not be updated.')
  
    return redirect(url_for('show_artist', artist_id=artist_id))

  else:
    for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
        
  
  return redirect(url_for('edit_artist_submission', artist_id=artist_id , form=form))


###################################################################################################################
###################################################################################################################






###################################################################################################################
###################################################################################################################
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  ## Done
  form = VenueForm()

  venue_data = Venue.query.get(venue_id)
  venue = {}
  venue["id"] = venue_id
  venue["name"] = venue_data.name
  venue["genres"] = venue_data.genres[1:-1].split(',')
  venue["address"] = venue_data.address
  venue["city"] = venue_data.city
  venue["state"] = venue_data.state
  venue["phone"] = venue_data.phone
  venue["website"] = venue_data.website_link
  venue["facebook_link"] = venue_data.facebook_link
  venue["seeking_talent"] = ( venue_data.seeking == 'true')
  venue["seeking_description"] = venue_data.detail_seeking
  venue["image_link"] = venue_data.image_link


  return render_template('forms/edit_venue.html', form=form, venue=venue)

###################################################################################################################
###################################################################################################################





###################################################################################################################
###################################################################################################################
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  ## Done
  form = VenueForm()  
  error = False
  if form.validate_on_submit():
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']  
        address = request.form['address']         
        phone = request.form['phone']      
        image_link = request.form['image_link'] 
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']

        try:
          if request.form['seeking_talent'] == 'y':
            seeking = True
        except:
          seeking = False
          
        detail_seeking = request.form['seeking_description']  

        ## I have to convert the form into a dictionary in order to extract all genre values
        genres = request.form.to_dict(flat=False)['genres']
    
        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.city = city
        venue.state = state
        venue.address = address
        venue.phone = phone
        venue.image_link = image_link
        venue.facebook_link = facebook_link
        venue.website_link = website_link
        venue.seeking = seeking
        venue.detail_seeking = detail_seeking
        venue.genres = genres
                      

        db.session.add(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
          db.session.close()
      
    if not error :
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully updated!')      
    
    else:
      
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + name + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))


  else:
    for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
  
  return redirect(url_for('edit_venue_submission', venue_id=venue_id , form=form))



###################################################################################################################
###################################################################################################################





#  Create Artist
#  ----------------------------------------------------------------

###################################################################################################################
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
###################################################################################################################


###################################################################################################################
###################################################################################################################
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  ##Done
  form = ArtistForm()
  error = False

  if form.validate_on_submit():
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']     
        phone = request.form['phone']      
        image_link = request.form['image_link'] 
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']
        try:
          if request.form['seeking_venue'] == 'y':
            seeking = True
        except:
          seeking = False
          
        detail_seeking = request.form['seeking_description']  

        ## I have to convert the form into a dictionary in order to extract all genre values
        genres = request.form.to_dict(flat=False)['genres']
    
        artist = Artist(name = name,
                      city = city,
                      state = state,
                      phone = phone,
                      image_link = image_link,
                      facebook_link = facebook_link,
                      website_link = website_link,
                      seeking = seeking,
                      detail_seeking = detail_seeking,
                      genres = genres
                      )

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
          db.session.close()
      
    if not error :
        # on successful db insert, flash success
        flash('Artist ' + name + ' was successfully listed!')      
    
    else:
      
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + name + ' could not be listed.')

    return render_template('pages/home.html')
  
  
  else:
    for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
  
  return render_template('forms/new_artist.html', form=form)


  

###################################################################################################################
###################################################################################################################

#  Shows
#  ----------------------------------------------------------------

###################################################################################################################
###################################################################################################################
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  ##Done

  stmt = select(Show)
  result = db.session.execute(stmt).all()
  
  data = []
  
  #for loop to go through elements of result
  for row in result:
    
    show_dict = {}
    
    str_row = str(row._mapping['Show'])
    Rowlist = str_row.split(',')
    
    venue_id = int(Rowlist[0])
    
    ###Extract Venue Name
    venue_name_row = Venue.query.with_entities(Venue.name).filter_by(id=venue_id).first()
    venue_name_str = str(venue_name_row)
    venue_name = venue_name_str[2:-3]
    
    ###Extract Artist Name
    artist_id = int(Rowlist[1])
    artist_name_row = Artist.query.with_entities(Artist.name).filter_by(id=artist_id).first()
    artist_name_str = str(artist_name_row)
    artist_name = artist_name_str[2:-3]   

    ###Extract Artist image link

    artist_image_link_row = Artist.query.with_entities(Artist.image_link).filter_by(id=artist_id).first()
    artist_image_link_str = str(artist_image_link_row)
    artist_image_link = artist_image_link_str[2:-3]
    

    start_time = Rowlist[2]
    
    #add them to dict1
    show_dict["venue_id"] = venue_id
    show_dict["venue_name"] = venue_name        
    show_dict["artist_id"] = artist_id
    show_dict["artist_name"] = artist_name
    show_dict["artist_image_link"] = artist_image_link
    show_dict["start_time"] = start_time
     
    #add dict1 to data1
    data.append(show_dict)
    
  
  return render_template('pages/shows.html', shows=data)
###################################################################################################################
###################################################################################################################




###################################################################################################################
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
###################################################################################################################






###################################################################################################################
###################################################################################################################
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
  ##Done

  form = ShowForm()
  
  error = False
  if form.validate_on_submit():
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']         
        artist1 = Artist.query.get(artist_id)
        venue1 = Venue.query.get(venue_id)
        
        show1 = Show(datetime = start_time)
        

        show1.artist = artist1
        show1.venue = venue1
        venue1.artists.append(show1)
        artist1.venues.append(show1)


        db.session.add(show1)
        db.session.add(venue1)
        db.session.add(artist1)
        db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
          db.session.close()
      
    if not error :
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return render_template('pages/home.html')     
    
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.') 
    
    return render_template('pages/home.html')  
  
  
  else:
    for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
  
             
  return render_template('forms/new_show.html', form=form)



  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

###################################################################################################################
###################################################################################################################


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
    app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)

