import os
import dbconfig as cfg

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
USER = cfg.postgressql['user']
PASSWD = cfg.postgressql['passwd']
HOST = cfg.postgressql['host']
PORT = cfg.postgressql['port']
DB = cfg.postgressql['db']

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWD}@{HOST}:{PORT}/{DB}'
SQLALCHEMY_TRACK_MODIFICATIONS = False