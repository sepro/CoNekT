import os
basedir = os.path.abspath(os.path.dirname(__file__))


DEBUG = True
TESTING = True

ADMIN_PASSWORD = 'admin'

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db', 'planet.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migration')

SECRET_KEY = 'change me !'
