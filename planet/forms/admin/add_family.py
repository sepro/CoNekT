from flask_wtf import Form
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddFamiliesForm(Form):
    method_description = StringField('Description', [InputRequired])
    source = SelectField('Source', choices=[('plaza', 'PLAZA csv'), ('mcl', 'MCL'), ('orthofinder', 'OrthoFinder')])
    file = FileField()

