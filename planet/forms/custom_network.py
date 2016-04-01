from flask_wtf import Form
from wtforms import TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired

from planet.models.expression_networks import ExpressionNetworkMethod


class CustomNetworkForm(Form):
    method_id = SelectField('method', coerce=int)
    probes = TextAreaField('probes', [InputRequired()])

    def populate_method(self):
        self.method_id.choices = [(s.id, s.description) for s in ExpressionNetworkMethod.query.order_by(ExpressionNetworkMethod.description)]

