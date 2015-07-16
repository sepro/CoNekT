from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask.ext.login import LoginManager


# Set up app, database and login manager before importing models and controllers
# Important for db_create script

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main'

from planet.controllers.main import main

app.register_blueprint(main)



