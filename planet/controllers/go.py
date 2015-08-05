from flask import Blueprint, redirect, url_for, render_template, jsonify

from planet.models.go import GO


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

    output = {}

    for s in sequences:
        if s.species.code not in output.keys():
            output[s.species.code] = 1
        else:
            output[s.species.code] += 1

    return jsonify(output)
