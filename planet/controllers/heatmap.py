from flask import Blueprint, request, render_template, Response

import json

from planet import cache
from planet.forms.heatmap import HeatmapForm
from planet.models.expression.coexpression_clusters import CoexpressionCluster
from planet.models.expression.profiles import ExpressionProfile
from planet.models.relationships.sequence_cluster import SequenceCoexpressionClusterAssociation
from planet.models.sequences import Sequence

heatmap = Blueprint('heatmap', __name__)


@heatmap.route('/cluster/<cluster_id>')
@heatmap.route('/cluster/<cluster_id>/<option>')
@cache.cached()
def heatmap_cluster(cluster_id, option='zlog'):
    """
    Controller that gets expression profiles for all members of a co-expression cluster and renders it as a
    tabular heatmap

    :param cluster_id: Internal ID of the cluster
    :param option: zlog or raw
    """
    cluster = CoexpressionCluster.query.get(cluster_id)
    associations = SequenceCoexpressionClusterAssociation.query.filter_by(coexpression_cluster_id=cluster_id).all()

    probes = [a.probe for a in associations]

    current_heatmap = ExpressionProfile.get_heatmap(cluster.method.network_method.species_id, probes,
                                                    zlog=(option == 'zlog'),
                                                    raw=(option == 'raw')
                                                    )

    return render_template("expression_heatmap.html",
                           order=current_heatmap['order'],
                           profiles=current_heatmap['heatmap_data'],
                           cluster=cluster,
                           zlog=(1 if option == 'zlog' else 0),
                           raw=(1 if option == 'raw' else 0))


@heatmap.route('/', methods=['GET', 'POST'])
def heatmap_main():
    """
    Renders a heatmap based on a set of probes passed using a POST request
    """
    form = HeatmapForm(request.form)
    form.populate_species()
    form.populate_options()

    if request.method == 'POST':
        terms = request.form.get('probes').split()
        species_id = request.form.get('species_id')

        option = request.form.get('options')
        print(option)

        probes = terms

        # also do search by gene ID
        sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

        for s in sequences:
            for ep in s.expression_profiles:
                probes.append(ep.probe)

        # make probe list unique
        probes = list(set(probes))
        # TODO check if certain probes were not found and warn the user
        current_heatmap = ExpressionProfile.get_heatmap(species_id, probes,
                                                        zlog=(option == 'zlog'),
                                                        raw=(option == 'raw'))

        return render_template("expression_heatmap.html", order=current_heatmap['order'],
                               profiles=current_heatmap['heatmap_data'],
                               form=form,
                               zlog=1 if option == 'zlog' else 0,
                               raw=1 if option == 'raw' else 0)
    else:
        profiles = ExpressionProfile.query.filter(ExpressionProfile.sequence_id is not None).order_by(ExpressionProfile.species_id).limit(5).all()

        example = {
            'species_id': None,
            'probes': None,
            'options': 'zlog'
        }

        if len(profiles) > 0:
            example['species_id'] = profiles[0].species_id
            example['probes'] = ' '.join([p.sequence.name for p in profiles])

        return render_template("expression_heatmap.html", form=form, example=example)


@heatmap.route('/inchlib/j/<cluster_id>.json')
@cache.cached()
def heatmap_inchlib_json(cluster_id):
    cluster = CoexpressionCluster.query.get(cluster_id)
    associations = SequenceCoexpressionClusterAssociation.query.filter_by(coexpression_cluster_id=cluster_id).all()

    probes = [a.probe for a in associations]

    current_heatmap = ExpressionProfile.get_heatmap(cluster.method.network_method.species_id, probes)

    output = {"data": {
            "nodes": {a["name"]: {
                "count": 1,
                "distance": 0,
                "features": [round(a["values"][o], 3) if a["values"][o] != '-' else None for o in current_heatmap["order"]],
                "objects": [a["name"]]
            } for a in current_heatmap['heatmap_data']},
            "feature_names": [o for o in current_heatmap["order"]]
        }
    }

    return Response(json.dumps(output, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')


@heatmap.route('/inchlib/<cluster_id>')
@cache.cached()
def heatmap_inchlib(cluster_id):
    return render_template("inchlib_heatmap.html", cluster_id=cluster_id)
