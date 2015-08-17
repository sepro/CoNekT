from flask import Blueprint, redirect, url_for, render_template, Response

from planet.models.gene_families import GeneFamily
import json


family = Blueprint('family', __name__)


@family.route('/')
def family_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@family.route('/find/<family_name>')
def family_find(family_name):
    """
    Find a gene family based on the name and show the details for this family

    :param family_name: Name of the gene family
    """
    current_family = GeneFamily.query.filter_by(name=family_name).first_or_404()

    return render_template('family.html', family=current_family, count=current_family.sequences.count())


@family.route('/view/<family_id>')
def family_view(family_id):
    """
    Get a gene family based on the ID and show the details for this family

    :param family_id: ID of the gene family
    """
    current_family = GeneFamily.query.get_or_404(family_id)

    return render_template('family.html', family=current_family, count=current_family.sequences.count())


@family.route('/json/species/<family_id>')
def family_json_species(family_id):
    """
    Generates a JSON object with the species composition that can be rendered using Chart.js pie charts or doughnut
    plots

    :param family_id: ID of the family to render
    """
    current_family = GeneFamily.query.get_or_404(family_id)
    sequences = current_family.sequences.all()

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
