from flask import Blueprint, redirect, url_for, render_template, jsonify

from planet.models.interpro import Interpro


interpro = Blueprint('interpro', __name__)


@interpro.route('/')
def interpro_overview():
    return redirect(url_for('main.screen'))


@interpro.route('/find/<interpro_domain>')
def interpro_find(interpro_domain):
    current_interpro = Interpro.query.filter_by(label=interpro_domain).first_or_404()

    return render_template('interpro.html', interpro=current_interpro)


@interpro.route('/view/<interpro_id>')
def interpro_view(interpro_id):
    current_interpro = Interpro.query.get_or_404(interpro_id)

    return render_template('interpro.html', interpro=current_interpro)


@interpro.route('/json/species/<interpro_id>')
def interpro_json_species(interpro_id):
    current_interpro = Interpro.query.get_or_404(interpro_id)
    sequences = current_interpro.sequences.all()

    output = {}

    for s in sequences:
        if s.species.code not in output.keys():
            output[s.species.code] = 1
        else:
            output[s.species.code] += 1

    return jsonify(output)
