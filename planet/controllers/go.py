from flask import Blueprint, redirect, url_for, render_template, Response, g

from planet.models.go import GO
from planet.models.sequences import Sequence
import json
from utils.benchmark import benchmark

from sqlalchemy.orm import joinedload, defer

go = Blueprint('go', __name__)


@go.route('/')
def go_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@go.route('/find/<go_label>')
def go_find(go_label):
    """
    Find a go term based on the label and show the details for this term

    :param go_label: Label of the GO term
    """
    current_go = GO.query.filter_by(label=go_label).first_or_404()
    seqIDs = {}
    sequences = current_go.sequences.with_entities(Sequence.id).all()

    for s in sequences:
        seqIDs[s.id] = ""

    sequence_count = len(seqIDs)

    return render_template('go.html', go=current_go, count=sequence_count)


@go.route('/view/<go_id>')
def go_view(go_id):
    """
    Get a go term based on the ID and show the details for this term

    :param go_id: ID of the go term
    """
    current_go = GO.query.get_or_404(go_id)
    seqIDs = {}
    sequences = current_go.sequences.with_entities(Sequence.id).all()

    for s in sequences:
        seqIDs[s.id] = ""

    sequence_count = len(seqIDs)

    return render_template('go.html', go=current_go, count=sequence_count)


@go.route('/sequences/<go_id>/')
@go.route('/sequences/<go_id>/<int:page>')
@benchmark
def go_sequences(go_id, page=1):
    """
    Returns a table with sequences with the selected go

    :param go_id: Internal ID of the GO term
    :param page: Page number
    """
    sequences = GO.query.get(go_id).sequences.options(defer('coding_sequence')).\
        group_by(Sequence.id).order_by(Sequence.name).paginate(page,
                                                               g.page_items,
                                                               False).items

    return render_template('pagination/sequences.html', sequences=sequences)


@go.route('/json/species/<go_id>')
@benchmark
def go_json_species(go_id):
    """
    Generates a JSON object with the species composition that can be rendered using Chart.js pie charts or doughnut
    plots

    :param go_id: ID of the go term to render
    """
    current_go = GO.query.get_or_404(go_id)
    sequences = current_go.sequences.options(defer('coding_sequence')).options(joinedload('species')).all()

    counts = {}

    for s in sequences:
        if s.species.code not in counts.keys():
            counts[s.species.code] = {}
            counts[s.species.code]["label"] = s.species.name
            counts[s.species.code]["color"] = s.species.color
            counts[s.species.code]["highlight"] = s.species.highlight
            counts[s.species.code]["value"] = 1
        else:
            counts[s.species.code]["value"] += 1

    return Response(json.dumps([counts[s] for s in counts.keys()]), mimetype='application/json')

