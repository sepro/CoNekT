from flask_wtf import Form
from wtforms import StringField, SelectField, FloatField, BooleanField
from wtforms.validators import InputRequired

from planet.models.species import Species


class SearchSpecificProfilesForm(Form):
    species = SelectField('Species')
    methods = SelectField('Method')
    conditions = SelectField('Condition')
    cutoff = StringField('Cutoff')

    def populate_form(self):
        self.species.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        self.methods.choices = [(0, "Select species first")]
        self.conditions.choices = [(0, "Select method first")]

