from flask import Blueprint, redirect, url_for, render_template, Response

from planet.models.go import GO
import json


go = Blueprint('go', __name__)


@go.route('/')
def go_overview():
    return redirect(url_for('main.screen'))


@go.route('/find/<go_label>')
def go_find(go_label):
    current_go = GO.query.filter_by(label=go_label).first_or_404()

    return render_template('go.html', go=current_go)


@go.route('/view/<go_id>')
def go_view(go_id):
    current_go = GO.query.get_or_404(go_id)

    return render_template('go.html', go=current_go)


@go.route('/json/species/<go_id>')
def go_json_species(go_id):
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

