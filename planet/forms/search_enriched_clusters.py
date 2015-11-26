from flask_wtf import Form
from wtforms import StringField, SelectField, FloatField, BooleanField
from wtforms.validators import InputRequired

from planet.models.species import Species


class SearchEnrichedClustersForm(Form):
    species_id = SelectField('species', coerce=int)
    go_term = StringField('go_term', [InputRequired()])

    check_enrichment = BooleanField('Check enrichment?')
    check_p = BooleanField('Check enrichment?')
    check_corrected_p = BooleanField('Check enrichment?')

    min_enrichment = FloatField('min_enrichment', default=0.0)
    max_p = FloatField('max_p', default=0.05)
    max_corrected_p = FloatField('max_corrected_p', default=0.05)

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by('name')]
        self.species_id.choices.append((-1, "All Species"))

