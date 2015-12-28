from flask import Blueprint, request, render_template,flash
from sqlalchemy.orm import noload

from planet import cache
from planet.models.sequences import Sequence
from planet.models.expression_profiles import ExpressionProfile
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.models.coexpression_clusters import CoexpressionCluster

from planet.forms.profile_comparison import ProfileComparisonForm

from planet.helpers.chartjs import prepare_profiles

import json

profile_comparison = Blueprint('profile_comparison', __name__)


@profile_comparison.route('/cluster/<cluster_id>')
@profile_comparison.route('/cluster/<cluster_id>/<int:normalize>')
@cache.cached()
def profile_comparison_cluster(cluster_id, normalize=0):
    """
    This will get all the expression profiles for members of given cluster and plot them

    :param cluster_id: internal id of the cluster to visualize
    """
    cluster = CoexpressionCluster.query.get(cluster_id)
    associations = SequenceCoexpressionClusterAssociation.query.\
        filter_by(coexpression_cluster_id=cluster_id).\
        options(noload(SequenceCoexpressionClusterAssociation.sequence)).\
        all()

    probes = [a.probe for a in associations]

    # get max 51 profiles, only show the first 50 (the extra one is fetched to throw the warning)
    profiles = ExpressionProfile.get_profiles(cluster.method.network_method.species_id, probes, limit=51)

    if len(profiles) > 50:
        flash("To many profiles in this cluster only showing the first 50", 'warning')

    profile_chart = prepare_profiles(profiles[:50], True if normalize == 1 else False)

    return render_template("expression_profile_comparison.html",
                           profiles=json.dumps(profile_chart))


@profile_comparison.route('/', methods=['GET', 'POST'])
def profile_comparison_main():
    """
    Profile comparison tool, accepts a species and a list of probes and plots the profiles for the selected
    """
    form = ProfileComparisonForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        probes = request.form.get('probes').split()
        species_id = request.form.get('species_id')
        normalize = True if request.form.get('normalize') == 'y' else False

        # get max 51 profiles, only show the first 50 (the extra one is fetched to throw the warning)
        profiles = ExpressionProfile.get_profiles(species_id, probes, limit=51)

        if len(profiles) > 50:
            flash("To many profiles in this cluster only showing the first 50", 'warning')

        profile_chart = prepare_profiles(profiles[:50], normalize)

        return render_template("expression_profile_comparison.html",
                               profiles=json.dumps(profile_chart), form=form)
    else:
        return render_template("expression_profile_comparison.html", form=form)
