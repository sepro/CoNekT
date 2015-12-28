from flask_wtf import Form
from wtforms import StringField, SelectField, FloatField, BooleanField
from wtforms.validators import InputRequired

from planet.models.coexpression_clusters import CoexpressionClusteringMethod


class SearchEnrichedClustersForm(Form):
    method = SelectField('Method', coerce=int)
    go_term = StringField('go_term', [InputRequired()])

    check_enrichment = BooleanField('Check enrichment?')
    check_p = BooleanField('Check enrichment?')
    check_corrected_p = BooleanField('Check enrichment?')

    min_enrichment = FloatField('min_enrichment', default=0.0)
    max_p = FloatField('max_p', default=0.05)
    max_corrected_p = FloatField('max_corrected_p', default=0.05)

    def populate_method(self):
        self.method.choices = [(s.id, s.method) for s in CoexpressionClusteringMethod.query.order_by(CoexpressionClusteringMethod.method)]
        self.method.choices.append((-1, "All Species"))

