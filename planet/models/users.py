from werkzeug.security import generate_password_hash, check_password_hash
from planet import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    password_hash = db.Column(db.Text)
    email = db.Column(db.Text)
    reset_key = db.Column(db.Text)
    is_admin = db.Column(db.Boolean)
    is_banned = db.Column(db.Boolean)
    wants_newsletter = db.Column(db.Boolean)
    registered = db.Column(db.DateTime)

    def __init__(self, username, password, email, reset_key='', is_admin=False, is_banned=False,
                 registered=datetime.now().replace(microsecond=0)):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.reset_key = reset_key
        self.is_admin = is_admin
        self.is_banned = is_banned
        self.registered = registered
        self.wants_newsletter = False

    def __repr__(self):
        return '<User %d>' % self.id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        return self.is_admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
