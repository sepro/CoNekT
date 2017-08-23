import json

from flask import Blueprint, redirect, url_for, render_template, Response
from sqlalchemy.orm import undefer

from planet import cache
from planet.helpers.chartjs import prepare_expression_profile, prepare_profile_comparison
from planet.models.condition_tissue import ConditionTissue
from planet.models.expression.profiles import ExpressionProfile
from planet.models.expression.networks import ExpressionNetwork
from planet.models.expression.specificity import ExpressionSpecificityMethod

expression_profile = Blueprint('expression_profile', __name__)


@expression_profile.route('/')
def expression_profile_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@expression_profile.route('/view/<profile_id>')
@cache.cached()
def expression_profile_view(profile_id):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)

    expression_specificity_methods = ExpressionSpecificityMethod.query.filter(ExpressionSpecificityMethod.species_id == current_profile.species_id).all()

    tissues = []

    for esm in expression_specificity_methods:
        if esm.condition_tissue is not None:
            tissues.append({'id': esm.condition_tissue.id,
                            'name': esm.description,
                            'description': esm.condition_tissue.description})

    return render_template("expression_profile.html", profile=current_profile, tissues=tissues)


@expression_profile.route('/modal/<profile_id>')
@cache.cached()
def expression_profile_modal(profile_id):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)

    return render_template("modals/expression_profile.html", profile=current_profile)


@expression_profile.route('/find/<probe>')
@expression_profile.route('/find/<probe>/<species_id>')
@cache.cached()
def expression_profile_find(probe, species_id=None):
    """
    Gets expression profile data from the database and renders it.

    :param probe: Name of the probe
    :param species_id: Species ID is required to ensure a unique hit
    """
    current_profile = ExpressionProfile.query.filter_by(probe=probe)

    if species_id is not None:
        current_profile = current_profile.filter_by(species_id=species_id)

    first_profile = current_profile.first_or_404()

    return redirect(url_for('expression_profile.expression_profile_view', profile_id=first_profile.id))


@expression_profile.route('/compare/<first_profile_id>/<second_profile_id>')
@expression_profile.route('/compare/<first_profile_id>/<second_profile_id>/<int:normalize>')
@cache.cached()
def expression_profile_compare(first_profile_id, second_profile_id, normalize=0):
    """
    Gets expression profile data from the database and renders it.

    :param first_profile_id: internal ID of the first profile
    :param second_profile_id: internal ID of the second profile
    :param normalize: 1 to normalize profiles (to max value), 0 to disable
    :return:
    """
    first_profile = ExpressionProfile.query.get_or_404(first_profile_id)
    second_profile = ExpressionProfile.query.get_or_404(second_profile_id)

    pcc = None
    hrr = None

    networks = ExpressionNetwork.query.filter(ExpressionNetwork.sequence_id == first_profile.sequence_id).all()

    for n in networks:
        data = json.loads(n.network)
        for link in data:
            if "gene_id" in link.keys() and link["gene_id"] == second_profile.sequence_id:
                if "link_pcc" in link.keys():
                    pcc = link["link_pcc"] if pcc is None or pcc < link["link_pcc"] else pcc
                if "hrr" in link.keys():
                    hrr = link["hrr"] if hrr is None or hrr > link["hrr"] else hrr

    return render_template("compare_profiles.html",
                           first_profile=first_profile,
                           second_profile=second_profile,
                           normalize=normalize,
                           pcc=pcc,
                           hrr=hrr)


@expression_profile.route('/compare_probes/<probe_a>/<probe_b>/<int:species_id>')
@expression_profile.route('/compare_probes/<probe_a>/<probe_b>/<int:species_id>/<int:normalize>')
@cache.cached()
def expression_profile_compare_probes(probe_a, probe_b, species_id, normalize=0):
    """
    Gets expression profile data from the database and renders it.

    :param probe_a: name of the first probe
    :param probe_b: name of the second probe
    :param species_id: internal id of the species the probes are linked with
    :param normalize: 1 to normalize profiles (to max value), 0 to disable
    :return:
    """
    first_profile = ExpressionProfile.query.filter_by(probe=probe_a).filter_by(species_id=species_id).first_or_404()
    second_profile = ExpressionProfile.query.filter_by(probe=probe_b).filter_by(species_id=species_id).first_or_404()

    pcc = None
    hrr = None

    networks = ExpressionNetwork.query.filter(ExpressionNetwork.sequence_id == first_profile.sequence_id).all()

    for n in networks:
        data = json.loads(n.network)
        for link in data:
            if "gene_id" in link.keys() and link["gene_id"] == second_profile.sequence_id:
                if "link_pcc" in link.keys():
                    pcc = link["link_pcc"] if pcc is None or pcc < link["link_pcc"] else pcc
                if "hrr" in link.keys():
                    hrr = link["hrr"] if hrr is None or hrr > link["hrr"] else hrr

    return render_template("compare_profiles.html",
                           probe_a=probe_a,
                           probe_b=probe_b,
                           first_profile=first_profile,
                           second_profile=second_profile,
                           species_id=species_id,
                           normalize=normalize,
                           pcc=pcc,
                           hrr=hrr)


@expression_profile.route('/download/plot/<profile_id>')
@cache.cached()
def expression_profile_download_plot(profile_id):
    """
    Generates a tab-delimited table for off-line use

    :param profile_id: ID of the profile to render
    """
    current_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(profile_id)

    return Response(current_profile.table)


@expression_profile.route('/json/plot/<profile_id>')
@cache.cached()
def expression_profile_plot_json(profile_id):
    """
    Generates a JSON object that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    """
    current_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(profile_id)
    data = json.loads(current_profile.profile)

    plot = prepare_expression_profile(data, show_sample_count=True)

    return Response(json.dumps(plot), mimetype='application/json')


@expression_profile.route('/json/plot/<profile_id>/<condition_tissue_id>')
@cache.cached()
def expression_profile_plot_tissue_json(profile_id, condition_tissue_id):
    """
    Generates a JSON object that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    :param condition_tissue_id: ID of the condition to tissue conversion to be used
    """
    current_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(profile_id)
    data = current_profile.tissue_profile(condition_tissue_id)

    plot = prepare_expression_profile(data)

    return Response(json.dumps(plot), mimetype='application/json')


@expression_profile.route('/json/compare_plot/<first_profile_id>/<second_profile_id>')
@expression_profile.route('/json/compare_plot/<first_profile_id>/<second_profile_id>/<int:normalize>')
@cache.cached()
def expression_profile_compare_plot_json(first_profile_id, second_profile_id, normalize=0):
    """
    Generates a JSON object with two profiles that can be rendered using Chart.js line plots

    :param first_profile_id:
    :param second_profile_id:
    :param normalize:
    :return:
    """
    first_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(first_profile_id)
    second_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(second_profile_id)
    data_first = json.loads(first_profile.profile)
    data_second = json.loads(second_profile.profile)

    plot = prepare_profile_comparison(data_first, data_second,
                                      (first_profile.probe, second_profile.probe),
                                      normalize=normalize)

    return Response(json.dumps(plot), mimetype='application/json')
