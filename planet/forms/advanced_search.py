from planet.models.species import Species

from flask_wtf import FlaskForm
from wtforms import Form, FormField, FieldList,StringField, SelectField, RadioField, TextAreaField
from wtforms.validators import InputRequired


class GOField(Form):
    go_term = StringField('go_term')


class InterProField(Form):
    interpro_domain = StringField('interpro_domain')


class AdvancedSequenceSearchForm(FlaskForm):
    species = SelectField('species', coerce=int)
    gene_ids = TextAreaField('gene list', render_kw={'placeholder': 'Enter a list of gene identifiers or names to filter'})

    terms_rules = RadioField('term_rules', choices=[('all', 'All'), ('any', 'Any'), ('exact', 'Exact')], default='all')
    terms = StringField('term')

    go_rules = RadioField('go_rules', choices=[('all', 'All'), ('any', 'Any')], default='all')
    go_terms = FieldList(FormField(GOField), min_entries=1)

    interpro_rules = RadioField('interpro_rules', choices=[('all', 'All'), ('any', 'Any')], default='all')
    interpro_domains = FieldList(FormField(InterProField), min_entries=1)

    def populate_species(self):
        self.species.choices = [(-1, 'Any'), (-1, '-'*20)] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
