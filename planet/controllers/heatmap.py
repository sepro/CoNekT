from flask import Blueprint, request, render_template

from planet import cache
from planet.models.expression_profiles import ExpressionProfile
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.models.coexpression_clusters import CoexpressionCluster
from planet.models.sequences import Sequence
from planet.forms.heatmap import HeatmapForm

heatmap = Blueprint('heatmap', __name__)


@heatmap.route('/cluster/<cluster_id>')
@cache.cached()
def heatmap_cluster(cluster_id):
    """
    Controller that gets expression profiles for all members of a co-expression cluster and renders it as a
    tabular heatmap

    :param cluster_id: Internal ID of the cluster
    :param species_id: Species ID
    """
    cluster = CoexpressionCluster.query.get(cluster_id)
    associations = SequenceCoexpressionClusterAssociation.query.filter_by(coexpression_cluster_id=cluster_id).all()

    probes = [a.probe for a in associations]

    current_heatmap = ExpressionProfile.get_heatmap(cluster.method.network_method.species_id, probes)

    return render_template("expression_heatmap.html",
                           order=current_heatmap['order'],
                           profiles=current_heatmap['heatmap_data'])


@heatmap.route('/', methods=['GET', 'POST'])
def heatmap_main():
    """
    Renders a heatmap based on a set of probes passed using a POST request
    """
    form = HeatmapForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        terms = request.form.get('probes').split()
        species_id = request.form.get('species_id')

        probes = terms

        # also do search by gene ID
        sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

        for s in sequences:
            for ep in s.expression_profiles:
                probes.append(ep.probe)

        # make probe list unique
        probes = list(set(probes))

        current_heatmap = ExpressionProfile.get_heatmap(species_id, probes)

        return render_template("expression_heatmap.html", order=current_heatmap['order'],
                               profiles=current_heatmap['heatmap_data'],
                               form=form)
    else:
        return render_template("expression_heatmap.html", form=form)
