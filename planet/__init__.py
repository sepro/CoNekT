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
login_manager.login_view = 'auth.login'

from planet.models.users import User

from planet.controllers.main import main
from planet.controllers.auth import auth

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')



