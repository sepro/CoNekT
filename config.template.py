"""
Configuration of the website and database.

Copy this file to config.py and change the settings accordingly
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask settings, make sure to set the SECRET_KEY and turn DEBUG and TESTING to False for production
DEBUG = True
TESTING = True

SECRET_KEY = 'change me !'

# Password for the initial admin account
ADMIN_PASSWORD = 'admin'
ADMIN_EMAIL = 'admin@web.com'

# Should the login system be included
LOGIN_ENABLED = True

# Database settings, database location and path to migration scripts
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db', 'planet.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migration')

# Collation type, NOCASE for sqlite, '' for MySQL
SQL_COLLATION = 'NOCASE'

# Settings for the FTP/bulk data
PLANET_FTP_DATA = os.path.join(basedir, 'ftp')

# Debug settings
DEBUG_TB_INTERCEPT_REDIRECTS = False
SQLALCHEMY_ECHO = DEBUG