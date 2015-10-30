from flask_wtf import Form
from wtforms import TextAreaField, SelectField
from wtforms.validators import InputRequired

from planet.models.species import Species


class ProfileComparisonForm(Form):
    species_id = SelectField('species', coerce=int)
    probes = TextAreaField('probes', [InputRequired()])

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by('name')]

