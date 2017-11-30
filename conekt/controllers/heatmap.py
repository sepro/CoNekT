from flask import Blueprint, request, render_template, Response

import json

from conekt import cache
from conekt.forms.heatmap import HeatmapForm, HeatmapComparableForm
from conekt.models.expression.coexpression_clusters import CoexpressionCluster
from conekt.models.expression.profiles import ExpressionProfile
from conekt.models.relationships.sequence_cluster import SequenceCoexpressionClusterAssociation
from conekt.models.sequences import Sequence
from conekt.models.trees import Tree
from conekt.models.gene_families import GeneFamily
from conekt.models.expression.cross_species_profile import CrossSpeciesExpressionProfile

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

    form2 = HeatmapComparableForm(request.form)
    form2.populate_options()

    profiles = ExpressionProfile.query.filter(ExpressionProfile.sequence_id is not None).order_by(ExpressionProfile.species_id).limit(5).all()

    example = {
        'species_id': None,
        'probes': None,
        'options': 'zlog'
    }

    if len(profiles) > 0:
        example['species_id'] = profiles[0].species_id
        example['probes'] = ' '.join([p.sequence.name for p in profiles])

    return render_template("expression_heatmap.html", form=form, form2=form2, example=example)


@heatmap.route('/results/default', methods=['POST'] )
def heatmap_custom_normal():
    form = HeatmapForm(request.form)
    form.populate_species()
    form.populate_options()

    terms = request.form.get('probes').split()
    species_id = request.form.get('species_id')

    option = request.form.get('options')

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
                           zlog=1 if option == 'zlog' else 0,
                           raw=1 if option == 'raw' else 0)


@heatmap.route('/results/comparable', methods=['POST'] )
def heatmap_custom_comparable():
    form = HeatmapComparableForm(request.form)
    form.populate_options()

    terms = request.form.get('probes').split()

    option = request.form.get('options')

    sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()
    sequence_ids = [s.id for s in sequences]

    current_heatmap = CrossSpeciesExpressionProfile().get_heatmap(*sequence_ids, option=option)

    return render_template("expression_heatmap.html", order=current_heatmap['order'],
                           profiles=current_heatmap['heatmap_data'],
                           zlog=1 if option == 'zlog' else 0,
                           raw=1 if option == 'raw' else 0)


@heatmap.route('/comparative/tree/<int:tree_id>')
@heatmap.route('/comparative/tree/<int:tree_id>/<option>')
@cache.cached()
def heatmap_comparative_tree(tree_id, option='raw'):
    tree = Tree.query.get_or_404(tree_id)
    sequences = tree.sequences
    sequence_ids = [s.id for s in sequences]

    heatmap_data = CrossSpeciesExpressionProfile().get_heatmap(*sequence_ids, option=option)

    return render_template("expression_heatmap.html", order=heatmap_data['order'],
                           profiles=heatmap_data['heatmap_data'],
                           zlog=1 if option == 'zlog' else 0,
                           raw=1 if option == 'raw' else 0,
                           tree=tree)


@heatmap.route('/comparative/family/<int:family_id>')
@heatmap.route('/comparative/family/<int:family_id>/<option>')
@cache.cached()
def heatmap_comparative_family(family_id, option='raw'):
    family = GeneFamily.query.get_or_404(family_id)
    sequences = family.sequences
    sequence_ids = [s.id for s in sequences]

    heatmap_data = CrossSpeciesExpressionProfile().get_heatmap(*sequence_ids, option=option)

    print(heatmap_data)

    return render_template("expression_heatmap.html", order=heatmap_data['order'],
                           profiles=heatmap_data['heatmap_data'],
                           zlog=1 if option == 'zlog' else 0,
                           raw=1 if option == 'raw' else 0,
                           family=family)


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
