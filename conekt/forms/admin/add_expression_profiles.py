from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField

from conekt.models.species import Species


class AddExpressionProfilesForm(FlaskForm):
    species_id = SelectField('Species', coerce=int)

    source = SelectField('Source', choices=[('lstrap', 'LSTrAP Expression Matrix')])

    matrix_file = FileField()
    annotation_file = FileField()
    order_colors_file = FileField()

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]
