from flask_wtf import FlaskForm
from wtforms import SelectField

from conekt.models.trees import TreeMethod


class ReconcileTreesForm(FlaskForm):
    tree_method_id = SelectField('Tree Method', coerce=int)

    def populate_methods(self):
        self.tree_method_id.choices = [(tm.id, tm.description) for tm in TreeMethod.query.all()]

