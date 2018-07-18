from flask import Blueprint, redirect, url_for, render_template, Response, g
from sqlalchemy.orm import joinedload

from conekt import cache
from conekt.helpers.chartjs import prepare_doughnut
from conekt.models.gene_families import GeneFamily
from conekt.models.sequences import Sequence

import json

family = Blueprint('family', __name__)


@family.route('/')
def family_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@family.route('/find/<family_name>')
@cache.cached()
def family_find(family_name):
    """
    Find a gene family based on the name and show the details for this family

    :param family_name: Name of the gene family
    """
    current_family = GeneFamily.query.filter_by(name=family_name).first_or_404()

    return redirect(url_for('family.family_view', family_id=current_family.id))


@family.route('/view/<family_id>')
def family_view(family_id):
    """
    Get a gene family based on the ID and show the details for this family

    :param family_id: ID of the gene family
    """
    current_family = GeneFamily.query.get_or_404(family_id)
    sequence_count = len(current_family.sequences.with_entities(Sequence.id).all())

    return render_template('family.html', family=current_family,
                           count=sequence_count,
                           xrefs=current_family.xrefs.all())


@family.route('/sequences/<family_id>/')
@family.route('/sequences/<family_id>/<int:page>')
@cache.cached()
def family_sequences(family_id, page=1):
    """
    Returns a table with sequences in the selected family

    :param family_id: Internal ID of the family
    :param page: Page number
    """
    sequences = GeneFamily.query.get(family_id).sequences.options(joinedload('species')).\
        order_by(Sequence.name).paginate(page,
                                         g.page_items,
                                         False).items

    return render_template('pagination/sequences.html', sequences=sequences)


@family.route('/sequences/table/<family_id>')
@cache.cached()
def family_sequences_table(family_id):
    """
    Returns a csv table with sequences in the selected family

    :param family_id: Internal ID of the family
    """
    sequences = GeneFamily.query.get(family_id).sequences.options(joinedload('species')).order_by(Sequence.name)

    return Response(render_template('tables/sequences.csv', sequences=sequences), mimetype='text/plain')


@family.route('/ecc_relations/<family_id>/')
@family.route('/ecc_relations/<family_id>/<int:page>')
@cache.cached()
def family_ecc_relations(family_id, page=1):
    f = GeneFamily.query.get(family_id)
    relations = f.ecc_associations_paginated(page, g.page_items)

    return render_template('pagination/ecc_relations.html', relations=relations)


@family.route('/json/species/<family_id>')
@cache.cached()
def family_json_species(family_id):
    """
    Generates a JSON object with the species composition that can be rendered using Chart.js pie charts or doughnut
    plots

    :param family_id: ID of the family to render
    """
    current_family = GeneFamily.query.get_or_404(family_id)
    sequences = current_family.sequences.options(joinedload('species')).all()

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

    plot = prepare_doughnut(counts)

    return Response(json.dumps(plot), mimetype='application/json')


@family.route('/tooltip/<family_id>')
@cache.cached()
def family_tooltip(family_id):
    """
    Get a family based on the ID and show the details for this sequence

    :param family_id: ID of the sequence
    """
    current_family = GeneFamily.query.get_or_404(family_id)

    return render_template('tooltips/family.html', family=current_family)


@family.route('/ajax/interpro/<family_id>')
@cache.cached()
def family_interpro_ajax(family_id):
    f = GeneFamily.query.get(family_id)

    return render_template('async/interpro_stats.html', interpro_stats=f.interpro_stats)


@family.route('/ajax/go/<family_id>')
@cache.cached()
def family_go_ajax(family_id):
    f = GeneFamily.query.get(family_id)

    return render_template('async/go_stats.html', go_stats=f.go_stats)


@family.route('/ajax/family/<family_id>')
@cache.cached()
def family_family_ajax(family_id):
    f = GeneFamily.query.get(family_id)

    return render_template('async/family_stats.html',
                           family_stats={k: v for k, v in f.family_stats.items() if str(k) != str(family_id)})
