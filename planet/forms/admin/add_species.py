from flask_wtf import Form
from wtforms import StringField, RadioField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddSpeciesForm(Form):
    name = StringField('Scientific Name', [InputRequired()])
    code = StringField('Code', [InputRequired()])

    data_type = RadioField('Data type',
                           choices=[('genome', 'Genome'), ('transcriptome', 'Transcriptome')],
                           default='genome')

    color = StringField('Color', [InputRequired()])
    highlight = StringField('Highlight', [InputRequired()])

    fasta = FileField('Fasta')



