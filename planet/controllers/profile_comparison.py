from flask import Blueprint, request, render_template,flash

from planet.models.expression_profiles import ExpressionProfile
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.models.coexpression_clusters import CoexpressionCluster

from planet.forms.profile_comparison import ProfileComparisonForm

import json
from statistics import mean

profile_comparison = Blueprint('profile_comparison', __name__)


@profile_comparison.route('/cluster/<cluster_id>')
def profile_comparison_cluster(cluster_id):
    cluster = CoexpressionCluster.query.get(cluster_id)
    associations = SequenceCoexpressionClusterAssociation.query.filter_by(coexpression_cluster_id=cluster_id).all()

    probes = [a.probe for a in associations]

    # get max 51 profiles, only show the first 50 (the extra one is fetched to throw the warning)
    profiles = ExpressionProfile.get_profiles(cluster.method.network_method.species_id, probes, limit=51)

    labels = []
    datasets = []

    if len(profiles) > 0:
        data = json.loads(profiles[0].profile)
        labels = data['order']

    if len(profiles) > 50:
        flash("To many profiles in this cluster only showing the first 50", 'warning')

    for count, p in enumerate(profiles):
        if count > 50:
            break
        data = json.loads(p.profile)
        datasets.append({
            'label': p.probe if p.sequence_id is None else p.sequence.name + " (" + p.probe + ")",
            'strokeColor': 'rgba(175,175,175,0.2)',
            'pointStrokeColor': 'rgba(220,220,220,0)',
            'fillColor': 'rgba(220,220,220,0.1)',
            'pointHighlightStroke': 'rgba(220,220,220,0)',
            'pointColor': 'rgba(220,220,220,0)',
            'pointHighlightFill': 'rgba(220,220,220,0)',
            'data': [mean(data['data'][label]) for label in labels]
        })

    return render_template("expression_profile_comparison.html",
                           profiles=json.dumps({'labels': labels, 'datasets': datasets}))


@profile_comparison.route('/', methods=['GET', 'POST'])
def profile_comparison_main():
    form = ProfileComparisonForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        probes = request.form.get('probes').split()
        species_id = request.form.get('species_id')

        # get max 51 profiles, only show the first 50 (the extra one is fetched to throw the warning)
        profiles = ExpressionProfile.get_profiles(species_id, probes, limit=51)

        labels = []
        datasets = []

        if len(profiles) > 0:
            data = json.loads(profiles[0].profile)
            labels = data['order']

        if len(profiles) > 50:
            flash("To many profiles in this cluster only showing the first 50", 'warning')

        for count, p in enumerate(profiles):
            if count > 50:
                break
            data = json.loads(p.profile)
            datasets.append({
                'label': p.probe if p.sequence_id is None else p.sequence.name + " (" + p.probe + ")",
                'strokeColor': 'rgba(175,175,175,0.2)',
                'pointStrokeColor': 'rgba(220,220,220,0)',
                'fillColor': 'rgba(220,220,220,0.1)',
                'pointHighlightStroke': 'rgba(220,220,220,0)',
                'pointColor': 'rgba(220,220,220,0)',
                'pointHighlightFill': 'rgba(220,220,220,0)',
                'data': [mean(data['data'][label]) for label in labels]
            })

        return render_template("expression_profile_comparison.html",
                               profiles=json.dumps({'labels': labels, 'datasets': datasets}), form=form)
    else:
        return render_template("expression_profile_comparison.html", form=form)
