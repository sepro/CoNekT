from flask_caching import Cache
from flask_compress import Compress
from flask_debugtoolbar import DebugToolbarExtension
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from planet.flask_blast import BlastThread

__all__ = ['db', 'login_manager', 'cache', 'htmlmin', 'blast_thread', 'compress']

db = SQLAlchemy()
login_manager = LoginManager()
toolbar = DebugToolbarExtension()
cache = Cache()
htmlmin = HTMLMIN()
blast_thread = BlastThread()
compress = Compress()