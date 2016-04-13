"""
Configuration of the website and database.

Copy this file to config.py and change the settings accordingly
"""
import os
import tempfile
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask settings, make sure to set the SECRET_KEY and turn DEBUG and TESTING to False for production
DEBUG = True
TESTING = True

SECRET_KEY = 'change me !'

# Login settings + admin account
LOGIN_ENABLED = True
ADMIN_PASSWORD = 'admin'
ADMIN_EMAIL = 'admin@web.com'

# Database settings, database location and path to migration scripts
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db', 'planet.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migration')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = DEBUG

# Collation type, NOCASE for sqlite, '' for MySQL
SQL_COLLATION = 'NOCASE' if SQLALCHEMY_DATABASE_URI.startswith('sqlite') else ''

# Settings for the FTP/bulk data
PLANET_FTP_DATA = os.path.join(basedir, 'ftp')

# Settings for Cache
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 120
CACHE_THRESHOLD = 10000

# Minify pages when debug is off
MINIFY_PAGE = not DEBUG

# BLAST settings
BLAST_ENABLED = False
BLAST_TMP_DIR = tempfile.mkdtemp()
BLASTP_PATH = ''
BLASTP_DB_PATH = ''
BLASTN_PATH = ''
BLASTN_DB_PATH = ''
BLASTP_CMD = BLASTP_PATH + ' -db ' + BLASTP_DB_PATH + ' -query <IN> -out <OUT> -outfmt 6 -num_threads 1'
BLASTN_CMD = BLASTN_PATH + ' -db ' + BLASTN_DB_PATH + ' -query <IN> -out <OUT> -outfmt 6 -num_threads 1'

# Debug settings
DEBUG_TB_INTERCEPT_REDIRECTS = False

