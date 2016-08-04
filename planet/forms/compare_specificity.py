from flask_wtf import Form
from wtforms import StringField, SelectField, FloatField, BooleanField
from wtforms.validators import InputRequired

from planet.models.species import Species


class CompareSpecificityForm(Form):
    speciesa = SelectField('Speciesa')
    methodsa = SelectField('Methoda')
    conditionsa = SelectField('Conditiona')
    cutoffa = StringField('Cutoffa')

    speciesb = SelectField('Speciesa')
    methodsb = SelectField('Methoda')
    conditionsb = SelectField('Conditiona')
    cutoffb = StringField('Cutoffa')

    def populate_form(self):
        self.speciesa.choices = [(0, "Select species")] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        self.methodsa.choices = [(0, "Select species first")]
        self.conditionsa.choices = [(0, "Select method first")]
        self.speciesb.choices = [(0, "Select species")] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        self.methodsb.choices = [(0, "Select species first")]
        self.conditionsb.choices = [(0, "Select method first")]

