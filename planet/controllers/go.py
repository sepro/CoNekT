from flask import Blueprint, redirect, url_for, render_template, Response, g

from planet.models.go import GO
import json


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

    return render_template('go.html', go=current_go, count=current_go.sequences.count())


@go.route('/view/<go_id>')
def go_view(go_id):
    """
    Get a go term based on the ID and show the details for this term

    :param go_id: ID of the go term
    """
    current_go = GO.query.get_or_404(go_id)

    return render_template('go.html', go=current_go, count=current_go.sequences.count())


@go.route('/sequences/<go_id>/')
@go.route('/sequences/<go_id>/<int:page>')
def go_sequences(go_id, page=1):
    sequences = GO.query.get(go_id).sequences.paginate(page,
                                                       g.page_items,
                                                       False).items

    return render_template('pages/sequences.html', sequences=sequences)


@go.route('/json/species/<go_id>')
def go_json_species(go_id):
    """
    Generates a JSON object with the species composition that can be rendered using Chart.js pie charts or doughnut
    plots

    :param go_id: ID of the go term to render
    """
    current_go = GO.query.get_or_404(go_id)
    sequences = current_go.sequences.all()

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

