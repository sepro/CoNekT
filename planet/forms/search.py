from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class BasicSearchForm(FlaskForm):
    terms = StringField('Terms', [InputRequired()])
