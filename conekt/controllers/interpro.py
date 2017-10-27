from flask import Blueprint, redirect, url_for, render_template, Response, g
from sqlalchemy.orm import joinedload, noload

from conekt import cache
from conekt.helpers.chartjs import prepare_doughnut
from conekt.models.interpro import Interpro
from conekt.models.sequences import Sequence

import json

interpro = Blueprint('interpro', __name__)


@interpro.route('/')
def interpro_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@interpro.route('/find/<interpro_domain>')
@cache.cached()
def interpro_find(interpro_domain):
    """
    Find an interpro domain based on the label and show the details for this domain

    :param interpro_domain: Name of the interpro domain
    """
    current_interpro = Interpro.query.filter_by(label=interpro_domain).first_or_404()

    return redirect(url_for('interpro.interpro_view', interpro_id=current_interpro.id))


@interpro.route('/view/<interpro_id>')
@cache.cached()
def interpro_view(interpro_id):
    """
    Get an interpro domain based on the ID and show the details for this domain

    :param interpro_id: ID of the interpro domain
    """
    current_interpro = Interpro.query.get_or_404(interpro_id)
    seqIDs = {}
    sequences = current_interpro.sequences.with_entities(Sequence.id).all()

    for s in sequences:
        seqIDs[s.id] = ""

    sequence_count = len(seqIDs)

    return render_template('interpro.html', interpro=current_interpro, count=sequence_count)


@interpro.route('/sequences/<interpro_id>/')
@interpro.route('/sequences/<interpro_id>/<int:page>')
@cache.cached()
def interpro_sequences(interpro_id, page=1):
    """
    Returns a table with sequences with the selected interpro domain

    :param interpro_id: Internal ID of the interpro domain
    :param page: Page number
    """
    sequences = Interpro.query.get(interpro_id).sequences.group_by(Sequence.id)\
        .options(joinedload('species'))\
        .paginate(page, g.page_items, False).items

    return render_template('pagination/sequences.html', sequences=sequences)


@interpro.route('/sequences/table/<interpro_id>')
@cache.cached()
def interpro_sequences_table(interpro_id):
    """
    Returns a csv table with all sequences with the selected interpro domain

    :param interpro_id: Internal ID of the interpro domain
    """
    sequences = Interpro.query.get(interpro_id).sequences.group_by(Sequence.id)\
        .options(joinedload('species'))\
        .order_by(Sequence.name)

    return Response(render_template('tables/sequences.csv', sequences=sequences), mimetype='text/plain')


@interpro.route('/json/species/<interpro_id>')
@cache.cached()
def interpro_json_species(interpro_id):
    """
    Generates a JSON object with the species composition that can be rendered using Chart.js pie charts or doughnut
    plots

    :param interpro_id: ID of the interpro domain to render
    """
    current_interpro = Interpro.query.get_or_404(interpro_id)
    sequences = current_interpro.sequences.options(noload('xrefs')).all()

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


@interpro.route('/ajax/interpro/<interpro_id>')
@cache.cached()
def interpro_interpro_ajax(interpro_id):
    current_interpro = Interpro.query.get(interpro_id)

    return render_template('async/interpro_stats.html',
                           interpro_stats={k: v for k, v in current_interpro.interpro_stats.items() if str(k) != str(interpro_id)})


@interpro.route('/ajax/go/<interpro_id>')
@cache.cached()
def interpro_go_ajax(interpro_id):
    current_interpro = Interpro.query.get(interpro_id)

    return render_template('async/go_stats.html', go_stats=current_interpro.go_stats)


@interpro.route('/ajax/family/<interpro_id>')
@cache.cached()
def interpro_family_ajax(interpro_id):
    current_interpro = Interpro.query.get(interpro_id)

    return render_template('async/family_stats.html', family_stats=current_interpro.family_stats)


@interpro.route('/tooltip/<interpro_id>')
@cache.cached()
def interpro_tooltip(interpro_id):
    """
    Get an interpro domain based and render in tooltip template

    :param interpro_id: ID of the interpro domain
    """
    current_interpro = Interpro.query.get_or_404(interpro_id)

    return render_template('tooltips/interpro.html', interpro=current_interpro)
