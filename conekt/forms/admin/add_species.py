from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField
from flask_wtf.file import FileRequired, FileField
from wtforms.validators import InputRequired, DataRequired


class AddSpeciesForm(FlaskForm):
    name = StringField("Scientific Name", [InputRequired()])
    code = StringField("Code", [InputRequired()])

    data_type = RadioField(
        "Data type",
        choices=[("genome", "Genome"), ("transcriptome", "Transcriptome")],
        default="genome",
    )

    color = StringField("Color", [InputRequired()])
    highlight = StringField("Highlight", [InputRequired()])

    description = TextAreaField("Description")

    fasta = FileField("Fasta")
