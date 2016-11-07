from flask_wtf import Form
from wtforms import StringField, SelectField
from flask_wtf.file import InputRequired, FileField

from planet.models.expression_networks import ExpressionNetworkMethod


class AddCoexpressionClustersForm(Form):
    network_id = SelectField('Network', coerce=int)
    description = StringField('Description', [InputRequired()])

    file = FileField()

    def populate_networks(self):
        self.network_id.choices = [(e.id, e.description) for e in ExpressionNetworkMethod.query.all()]
