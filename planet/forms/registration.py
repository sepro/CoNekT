from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Email

class RegistrationForm(Form):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [InputRequired()])
    email = StringField('Email', [InputRequired(), Email()])
