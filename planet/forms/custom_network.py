from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired

from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.gene_families import GeneFamilyMethod
from planet.models.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression_specificity import ExpressionSpecificityMethod


class CustomNetworkForm(FlaskForm):
    method_id = SelectField('method', coerce=int)
    probes = TextAreaField('probes', [InputRequired()])
    family_method = SelectField('family_method', coerce=int)
    cluster_method = SelectField('cluster_method', coerce=int)
    specificity_method = SelectField('specificity_method', coerce=int)

    def populate_method(self):
        self.method_id.choices = [(s.id, s.description) for s in ExpressionNetworkMethod.query.order_by(ExpressionNetworkMethod.description)]

        self.family_method.choices = [(m.id, m.method) for m in GeneFamilyMethod.query.order_by(GeneFamilyMethod.id)]
        self.cluster_method.choices = [(m.id, m.method) for m in CoexpressionClusteringMethod.query.order_by(CoexpressionClusteringMethod.id)]
        self.specificity_method.choices = [(m.id, m.description) for m in ExpressionSpecificityMethod.query.order_by(ExpressionSpecificityMethod.id)]