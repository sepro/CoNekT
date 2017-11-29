from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, BooleanField
from wtforms.validators import InputRequired

from conekt.models.expression.coexpression_clusters import CoexpressionClusteringMethod
from conekt.models.clades import Clade


class SearchEnrichedClustersForm(FlaskForm):
    method = SelectField('Method', coerce=int)
    go_term = StringField('go_term', [InputRequired()])

    check_enrichment = BooleanField('Check enrichment?')
    check_p = BooleanField('Check enrichment?')
    check_corrected_p = BooleanField('Check enrichment?')

    min_enrichment = FloatField('min_enrichment', default=0.0)
    max_p = FloatField('max_p', default=0.05)
    max_corrected_p = FloatField('max_corrected_p', default=0.05)

    enable_clade_enrichment = BooleanField('Enable clade/phylostrata enrichment?')
    clade = SelectField('Clade/Phylostrata', coerce=int)

    def populate_form(self):
        self.method.choices = [(s.id, "%s [%s]" % (s.method, s.network_method.species.name)) for s in CoexpressionClusteringMethod.query.order_by(CoexpressionClusteringMethod.method)]
        self.method.choices.append((-1, "All Species"))

        self.clade.choices = [(c.id, c.name) for c in Clade.query.order_by(Clade.name).all()]
