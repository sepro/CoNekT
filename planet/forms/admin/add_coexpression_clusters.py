from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.validators import InputRequired
from wtforms import StringField, SelectField

from planet.models.expression.networks import ExpressionNetworkMethod


class AddCoexpressionClustersForm(FlaskForm):
    network_id = SelectField('Network', coerce=int)
    description = StringField('Description', [InputRequired()])
    min_size = SelectField('Minimum cluster size', coerce=int, choices=[(i, i) for i in range(1, 11, 1)], default=10)

    file = FileField()

    def populate_networks(self):
        self.network_id.choices = [(e.id, e.description) for e in ExpressionNetworkMethod.query.all()]
