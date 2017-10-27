from flask_wtf import FlaskForm
from wtforms import SelectField

from conekt.models.species import Species


class ExportConditionForm(FlaskForm):
    species = SelectField('Species')
    methods = SelectField('Method')
    conditions = SelectField('Condition')

    def populate_form(self):
        self.species.choices = [(0, "Select species")] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        self.methods.choices = [(0, "Select species first")]
        self.conditions.choices = [(0, "Select species first")]

