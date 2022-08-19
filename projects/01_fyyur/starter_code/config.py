import os
import app
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database



# TODO IMPLEMENT DATABASE URL  ==>  DONE 
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:aicha@127.0.0.1:5432/project1'
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_SECRET_KEY= 'your_csrf_secret_key'
SECRET_KEY= 'your_secret_key'

