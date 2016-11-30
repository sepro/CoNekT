from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class AddCladesForm(FlaskForm):
    clades_json = TextAreaField('Clade definitions', [InputRequired()])


