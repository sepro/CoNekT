from flask_wtf import Form
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField, InputRequired

from planet.models.species import Species


class AddConditionSpecificityForm(Form):
    species_id = SelectField('Species', coerce=int)
    description = StringField('Description', [InputRequired()])

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]


class AddTissueSpecificityForm(Form):
    species_id = SelectField('Species', coerce=int)
    description = StringField('Description', [InputRequired()])

    file = FileField()

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]
