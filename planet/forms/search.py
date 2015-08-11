from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired


class BasicSearchForm(Form):
    terms = StringField('Terms', [InputRequired()])
