from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired

from conekt.models.species import Species
from conekt.models.gene_families import GeneFamilyMethod


class AddXRefsForm(FlaskForm):
    species_id = SelectField('species', coerce=int)
    platforms = SelectField('Platform', choices=[('plaza_3_dicots', 'PLAZA 3.0 Dicots'),
                                                 ('evex', 'EVEX'),
                                                 ('custom', 'Custom')])

    file = FileField()

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]


class AddXRefsFamiliesForm(FlaskForm):
    gene_family_method_id = SelectField('Gene Family Method', coerce=int)

    file = FileField()

    def populate_methods(self):
        self.gene_family_method_id.choices = [(gfm.id, gfm.method) for gfm in GeneFamilyMethod.query.all()]