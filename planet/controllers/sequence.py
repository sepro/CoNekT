from flask import g, Blueprint, flash, redirect, url_for, render_template, request


from planet.models.sequences import Sequence

sequence = Blueprint('sequence', __name__)

@sequence.route('/')
def sequence_overview():
    return "TEST OK"

@sequence.route('/view/<sequence_id>')
def sequence_view(sequence_id):
    current_sequence = Sequence.query.get_or_404(sequence_id)

    return render_template('sequence.html', sequence=current_sequence)
