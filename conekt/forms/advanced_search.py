from conekt.models.species import Species
from conekt.models.gene_families import GeneFamilyMethod

from flask_wtf import FlaskForm
from wtforms import Form, FormField, FieldList,StringField, SelectField, RadioField, TextAreaField, BooleanField
from wtforms.validators import InputRequired


class GOField(Form):
    go_term = StringField('go_term')


class InterProField(Form):
    interpro_domain = StringField('interpro_domain')


class AdvancedSequenceSearchForm(FlaskForm):
    species = SelectField('species', coerce=int)
    gene_ids = TextAreaField('gene list', render_kw={'placeholder': 'Enter a list of gene identifiers or names to filter'})

    terms_rules = RadioField('term_rules', choices=[('all', 'All'), ('any', 'Any'), ('exact', 'Exact')], default='all')
    adv_terms = StringField('term')

    go_rules = RadioField('go_rules', choices=[('all', 'All'), ('any', 'Any')], default='all')
    go_terms = FieldList(FormField(GOField), min_entries=1)
    include_predictions = BooleanField('include predictions')

    interpro_rules = RadioField('interpro_rules', choices=[('all', 'All'), ('any', 'Any')], default='all')
    interpro_domains = FieldList(FormField(InterProField), min_entries=1)

    gene_family_method = SelectField('gene_family_method', coerce=int)
    gene_families = TextAreaField('gene_families', render_kw={'placeholder': 'Enter a list of gene family identifiers to filter'})

    def populate_species(self):
        self.species.choices = [(-1, 'Any'), (-1, '-'*20)] + [(s.id, s.name) for
                                                              s in Species.query.order_by(Species.name).all()]

    def populate_gf_methods(self):
        self.gene_family_method.choices = [(-1, 'Disable'), (-1, '-'*20)] + [(m.id, m.method) for
                                                                             m in GeneFamilyMethod.query.all()]