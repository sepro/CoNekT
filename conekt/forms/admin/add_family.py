from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddFamiliesForm(FlaskForm):
    method_description = StringField('Description', [InputRequired])
    source = SelectField('Source', choices=[('mcl', 'MCL'), ('orthofinder', 'OrthoFinder'), ('general', 'General')])
    file = FileField()

