import json

from flask import Blueprint, render_template, Response

from conekt import cache
from conekt.helpers.cytoscape import CytoscapeHelper
from conekt.models.expression.coexpression_clusters import CoexpressionCluster
from conekt.models.gene_families import GeneFamilyMethod


graph_comparison = Blueprint('graph_comparison', __name__)


# TODO placeholder for the search function
# @graph_comparison.route('/')
# def graph_comparison_overview():
#     return "TEST"


@graph_comparison.route('/cluster/<int:one>/<int:two>')
@graph_comparison.route('/cluster/<int:one>/<int:two>/<int:family_method_id>')
@cache.cached()
def graph_comparison_cluster(one, two, family_method_id=1):
    """
    Controller to compare two clusters, requires a family_method_id and internal id's for two clusters. The order of the
    clusters is irrelevant. The actual network is fetched using .getJSON from graph_comparison_cluster_json

    :param one: internal id of the first cluster
    :param two: internal id of the second cluster
    :param family_method_id: internal id of the gene family method (used down stream for
    :return: html template with all UI elements for cytoscape.js that will fetch network data using .getJSON
    """
    cluster_one = CoexpressionCluster.query.get_or_404(one)
    cluster_two = CoexpressionCluster.query.get_or_404(two)

    cutoff = max([cluster_one.method.network_method.hrr_cutoff, cluster_two.method.network_method.hrr_cutoff])

    return render_template('expression_graph.html', cluster_one=cluster_one, cluster_two=cluster_two,
                           family_method_id=family_method_id, cutoff=cutoff)


@graph_comparison.route('/cluster/json/<int:one>/<int:two>')
@graph_comparison.route('/cluster/json/<int:one>/<int:two>/<int:family_method_id>')
@cache.cached()
def graph_comparison_cluster_json(one, two, family_method_id=None):
    """
    Controller that fetches network data from two clusters from the database, adds all essential information and merges
    the two networks. The function returns a JSON object compatible with cytoscape.js

    :param one: internal id of the first cluster
    :param two: internal id of the second cluster
    :param family_method_id: internal id of the gene family method (used down stream for coloring and connecting)
    :return: json object compatible with cytoscape.js and our UI elements
    """
    if family_method_id is None:
        family_method = GeneFamilyMethod.query.first()
        family_method_id = family_method.id

    network_one = CytoscapeHelper.parse_network(CoexpressionCluster.get_cluster(one))
    network_one = CytoscapeHelper.add_family_data_nodes(network_one, family_method_id)
    network_one = CytoscapeHelper.add_connection_data_nodes(network_one)

    network_two = CytoscapeHelper.parse_network(CoexpressionCluster.get_cluster(two))
    network_two = CytoscapeHelper.add_family_data_nodes(network_two, family_method_id)
    network_two = CytoscapeHelper.add_connection_data_nodes(network_two)

    output = CytoscapeHelper.merge_networks(network_one, network_two)
    output = CytoscapeHelper.add_lc_data_nodes(output)
    output = CytoscapeHelper.add_descriptions_nodes(output)

    return Response(json.dumps(output), mimetype='application/json')
