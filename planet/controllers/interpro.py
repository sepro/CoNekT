from flask import Blueprint, redirect, url_for, render_template, Response

from planet.models.interpro import Interpro
import json

interpro = Blueprint('interpro', __name__)


@interpro.route('/')
def interpro_overview():
    return redirect(url_for('main.screen'))


@interpro.route('/find/<interpro_domain>')
def interpro_find(interpro_domain):
    current_interpro = Interpro.query.filter_by(label=interpro_domain).first_or_404()

    return render_template('interpro.html', interpro=current_interpro, count=current_interpro.sequences.count())


@interpro.route('/view/<interpro_id>')
def interpro_view(interpro_id):
    current_interpro = Interpro.query.get_or_404(interpro_id)

    return render_template('interpro.html', interpro=current_interpro, count=current_interpro.sequences.count())


@interpro.route('/json/species/<interpro_id>')
def interpro_json_species(interpro_id):
    current_interpro = Interpro.query.get_or_404(interpro_id)
    sequences = current_interpro.sequences.all()

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

