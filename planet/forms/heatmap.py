from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired

from planet.models.species import Species


class HeatmapForm(FlaskForm):
    species_id = SelectField('species', coerce=int)
    probes = TextAreaField('probes', [InputRequired()])

    zlog = BooleanField('zlog transformation')

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]

