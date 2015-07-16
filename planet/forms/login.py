from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired

class LoginForm(Form):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    keep_logged = BooleanField('Remember me?')
