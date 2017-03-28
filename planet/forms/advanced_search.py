from planet.models.species import Species

from flask_wtf import FlaskForm
from wtforms import Form, FormField, FieldList,StringField, SelectField
from wtforms.validators import InputRequired


class GOField(Form):
    go_term = StringField('go_term')


class InterProField(Form):
    interpro_domain = StringField('interpro_domain')


class AdvancedSequenceSearchForm(FlaskForm):
    species = SelectField('species', coerce=int)
    any_field = StringField('any_field')
    all_field = StringField('all_field')

    go_terms = FieldList(FormField(GOField), min_entries=1)
    interpro_domains = FieldList(FormField(InterProField), min_entries=1)

    def populate_species(self):
        self.species.choices = [(-1, 'Any'), (-1, '-'*20)] + [(s.id, s.name) for s in Species.query.order_by(Species.name)]
