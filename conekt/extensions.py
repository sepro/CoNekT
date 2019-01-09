from functools import wraps
from flask import current_app, abort
from flask_caching import Cache
from flask_compress import Compress
from flask_debugtoolbar import DebugToolbarExtension
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager, current_user, user_unauthorized
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection

from conekt.flask_blast import BlastThread

__all__ = ['toolbar', 'db', 'login_manager', 'cache', 'htmlmin',
           'blast_thread', 'compress', 'whooshee', 'migrate', 'csrf']

db = SQLAlchemy()


def admin_required(fn):
    """
        Extend Flask-Login to support @admin_required decorator
        Requires User class to support is_admin() method
    """
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        try:
            if current_user.is_admin:
                return fn(*args, **kwargs)
        except Exception as e:
            print(str(e))
            raise

        user_unauthorized.send(current_app._get_current_object())
        abort(403)
    return decorated_view


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
        Will force sqlite contraint foreign keys
    """
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


login_manager = LoginManager()
toolbar = DebugToolbarExtension()
cache = Cache()
htmlmin = HTMLMIN()
blast_thread = BlastThread()
compress = Compress()
whooshee = Whooshee()
migrate = Migrate()
csrf = CSRFProtect()
