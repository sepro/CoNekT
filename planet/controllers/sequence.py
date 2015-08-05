from flask import Blueprint, redirect, url_for, render_template

from planet.models.sequences import Sequence


sequence = Blueprint('sequence', __name__)


@sequence.route('/')
def sequence_overview():
    return redirect(url_for('main.screen'))


@sequence.route('/find/<sequence_name>')
def sequence_find(sequence_name):
    current_sequence = Sequence.query.filter_by(name=sequence_name).first_or_404()

    return render_template('sequence.html', sequence=current_sequence)


@sequence.route('/view/<sequence_id>')
def sequence_view(sequence_id):
    current_sequence = Sequence.query.get_or_404(sequence_id)

    return render_template('sequence.html', sequence=current_sequence)
