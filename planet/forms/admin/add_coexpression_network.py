from flask_wtf import Form
from wtforms import StringField, RadioField, SelectField
from flask_wtf.file import FileRequired, FileField, InputRequired

from planet.models.species import Species


class AddCoexpressionNetworkForm(Form):
    species_id = SelectField('Species', coerce=int)

    description = StringField('Description', [InputRequired])

    limit = SelectField('Limit', coerce=int, choices=[(i, i) for i in range(10, 100, 10)], default=30)
    pcc_cutoff = SelectField('PCC-cutoff', coerce=float,
                             choices=[(i, i) for i in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]], default=0.7)

    file = FileField()

    def populate_species(self):
        self.species_id.choices = [(s.id, s.name) for s in Species.query.order_by(Species.name)]