from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, BooleanField
from wtforms.validators import InputRequired

from conekt.models.species import Species
from conekt.models.gene_families import GeneFamilyMethod


class CompareSpecificityForm(FlaskForm):
    family_method = SelectField('family_method')

    use_interpro = BooleanField('Use InterPro')

    speciesa = SelectField('Speciesa')
    methodsa = SelectField('Methoda')
    conditionsa = SelectField('Conditiona')
    cutoffa = StringField('Cutoffa')

    speciesb = SelectField('Speciesa')
    methodsb = SelectField('Methoda')
    conditionsb = SelectField('Conditiona')
    cutoffb = StringField('Cutoffa')

    def populate_form(self):
        self.family_method.choices = [(m.id, m.method) for m in GeneFamilyMethod.query.order_by(GeneFamilyMethod.id)]
        self.speciesa.choices = [(0, "Select species")] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        self.methodsa.choices = [(0, "Select species first")]
        self.conditionsa.choices = [(0, "Select method first")]
        self.speciesb.choices = [(0, "Select species")] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
        self.methodsb.choices = [(0, "Select species first")]
        self.conditionsb.choices = [(0, "Select method first")]

