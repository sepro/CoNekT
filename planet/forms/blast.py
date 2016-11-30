from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField
from wtforms.validators import InputRequired


class BlastForm(FlaskForm):
    blast_type = SelectField('blast_type')
    fasta = TextAreaField('fasta', [InputRequired()])

    def populate_blast_types(self):
        self.blast_type.choices = [('blastp',  'blastp'), ('blastn', 'blastn')]
