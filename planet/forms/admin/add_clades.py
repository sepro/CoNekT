from flask_wtf import Form
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class AddCladesForm(Form):
    clades_json = TextAreaField('Clade definitions', [InputRequired()])


