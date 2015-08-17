from flask import Blueprint, redirect, url_for, render_template

from planet.models.sequences import Sequence


sequence = Blueprint('sequence', __name__)


@sequence.route('/')
def sequence_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@sequence.route('/find/<sequence_name>')
def sequence_find(sequence_name):
    """
    Find a sequence based on the name and show the details for this sequence (useful for incoming links from other
    platforms)

    :param sequence_name: Name of the sequence
    """
    current_sequence = Sequence.query.filter_by(name=sequence_name).first_or_404()

    return render_template('sequence.html', sequence=current_sequence)


@sequence.route('/view/<sequence_id>')
def sequence_view(sequence_id):
    """
    Get a sequence based on the ID and show the details for this sequence

    :param sequence_id: ID of the sequence
    """
    current_sequence = Sequence.query.get_or_404(sequence_id)


    return render_template('sequence.html', sequence=current_sequence)
