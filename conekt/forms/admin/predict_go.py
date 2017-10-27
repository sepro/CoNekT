from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from wtforms import StringField, SelectField

from conekt.models.expression.networks import ExpressionNetworkMethod


class PredictGOForm(FlaskForm):
    network_id = SelectField('Network', coerce=int)
    description = StringField('Description', [InputRequired()])
    p_cutoff = SelectField('p-value cutoff', coerce=int, choices=[(i, i) for i in [0.001, 0.01, 0.05]], default=0.05)

    def populate_networks(self):
        self.network_id.choices = [(e.id, str(e))
                                   for e in ExpressionNetworkMethod.query.all()]
