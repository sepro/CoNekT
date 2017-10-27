from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField
from wtforms.validators import InputRequired

from conekt.models.expression.coexpression_clusters import CoexpressionClusteringMethod
from conekt.models.expression.networks import ExpressionNetworkMethod
from conekt.models.expression.specificity import ExpressionSpecificityMethod
from conekt.models.gene_families import GeneFamilyMethod


class CustomNetworkForm(FlaskForm):
    method_id = SelectField('method', coerce=int)
    probes = TextAreaField('probes', [InputRequired()])
    family_method = SelectField('family_method', coerce=int)
    cluster_method = SelectField('cluster_method', coerce=int)
    specificity_method = SelectField('specificity_method', coerce=int)

    def populate_method(self):
        self.method_id.choices = [(0, 'Select method')]

        self.family_method.choices = [(m.id, m.method) for m in GeneFamilyMethod.query.order_by(GeneFamilyMethod.id)]
        self.cluster_method.choices = [(0, 'Select method first')]
        self.specificity_method.choices = [(0, 'Select method first')]