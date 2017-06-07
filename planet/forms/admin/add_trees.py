from flask_wtf import FlaskForm
from wtforms import TextAreaField, FileField, SelectField
from wtforms.validators import InputRequired

from planet.models.gene_families import GeneFamilyMethod


class AddTreesForm(FlaskForm):
    gene_family_method_id = SelectField('Gene Family Method', coerce=int)
    description = TextAreaField('Description', [InputRequired()])

    tree_directory = FileField()


    def populate_methods(self):
        self.gene_family_method_id.choices = [(gfm.id, gfm.method) for gfm in GeneFamilyMethod.query.all()]

