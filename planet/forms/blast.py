from flask_wtf import Form
from wtforms import TextAreaField, SelectField
from wtforms.validators import InputRequired


class BlastForm(Form):
    blast_type = SelectField('blast_type')
    fasta = TextAreaField('fasta', [InputRequired()])

    def populate_blast_types(self):
        self.blast_type.choices = [(1,  'blastp'), (2, 'blastn')]
