from flask_wtf import Form
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddFamiliesForm(Form):
    source = SelectField('Source', choices=[('lstrap', 'LSTrAP Expression Matrix')])

    matrix_file = FileField()
    annotation_file = FileField()


