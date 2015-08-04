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

# Import all models here

from planet.models.users import User
from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.go import GO
from planet.models.interpro import Interpro
from planet.models.gene_families import GeneFamilyMethod, GeneFamily
from planet.models.coexpression_clusters import CoexpressionClusteringMethod, CoexpressionCluster

# Import all relationships (tables for many-to-many relationships)

import planet.models.relationships

# Import controllers and register as blueprint

from planet.controllers.main import main
from planet.controllers.auth import auth
from planet.controllers.sequence import sequence
from planet.controllers.species import species

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(sequence, url_prefix='/sequence')
app.register_blueprint(species, url_prefix='/species')
