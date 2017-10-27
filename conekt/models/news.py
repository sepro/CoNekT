from conekt import db, whooshee

from flask import Markup
from markdown import markdown
from datetime import datetime

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


@whooshee.register_model('message')
class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text(collation=SQL_COLLATION))
    posted = db.Column(db.DateTime)
    posted_by = db.Column(db.String(100))

    @property
    def message_markup(self):
        return Markup(markdown(self.message))

    @property
    def posted_formatted(self):
        return self.posted.strftime("%Y-%m-%d %H:%M")
