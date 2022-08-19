from app import app
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


db = SQLAlchemy(app)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
## Done

class Show(db.Model):
    __tablename__ = 'shows'
    
    venue_id = db.Column( db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    artist_id = db.Column( db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    datetime = db.Column( db.DateTime)  
    
    artist = db.relationship("Artist", back_populates="venues")
    venue = db.relationship("Venue", back_populates="artists")
    
    
    def __repr__(self) :
        return f'{self.venue_id},{self.artist_id},{self.datetime}' 
    




class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
 
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Done
    website_link = db.Column(db.String(120))
    seeking = db.Column(db.Boolean, nullable = False, default = False)
    detail_seeking = db.Column(db.String(500))
    genres = db.Column(db.String(120))

    artists = db.relationship("Show" , back_populates="venue")  

    

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Done
    website_link = db.Column(db.String(120))
    seeking = db.Column(db.Boolean, nullable = False, default = False)
    detail_seeking = db.Column(db.String(500))

    venues = db.relationship("Show" , back_populates="artist")  
