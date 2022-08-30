from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddFunctionalDataForm(FlaskForm):
    go = FileField("GO")
    interpro = FileField("InterPro")
