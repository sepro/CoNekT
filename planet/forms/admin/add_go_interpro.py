from flask_wtf import Form
from wtforms import StringField, RadioField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddFunctionalDataForm(Form):
    go = FileField('GO')
    interpro = FileField('InterPro')




