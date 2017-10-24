from flask_wtf import FlaskForm
from wtforms import StringField, SelectField

from planet.models.species import Species


class ExportConditionForm(FlaskForm):
    species = SelectField('Species')
    condition = StringField('Condition')

    def populate_form(self):
        self.species.choices = [(0, "Select species")] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        # self.condition.choices = [(0, "Select species first")]

