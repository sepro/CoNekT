from flask import Blueprint, render_template
from planet.models.coexpression_clusters import CoexpressionCluster

from planet.helpers.cytoscape import CytoscapeHelper

import json

graph_comparison = Blueprint('graph_comparison', __name__)


@graph_comparison.route('/')
def graph_comparison_overview():
    return "TEST"


@graph_comparison.route('/cluster/<int:one>/<int:two>')
def graph_comparison_cluster(one, two):
    cluster_one = CoexpressionCluster.query.get_or_404(one)
    cluster_two = CoexpressionCluster.query.get_or_404(two)

    return render_template('expression_graph.html', cluster_one=cluster_one, cluster_two=cluster_two)


@graph_comparison.route('/cluster/json/<int:one>/<int:two>')
def graph_comparison_cluster_json(one, two):
    output = []

    cluster_one = CoexpressionCluster.query.get_or_404(one)
    cluster_two = CoexpressionCluster.query.get_or_404(two)

    network_one = CytoscapeHelper.parse_network(CoexpressionCluster.get_cluster(one))
    network_one = CytoscapeHelper.add_family_data_nodes(network_one, 1)
    network_one = CytoscapeHelper.add_connection_data_nodes(network_one)
    network_two = CytoscapeHelper.parse_network(CoexpressionCluster.get_cluster(two))
    network_two = CytoscapeHelper.add_family_data_nodes(network_two, 1)
    network_two = CytoscapeHelper.add_connection_data_nodes(network_two)

    output = CytoscapeHelper.merge_networks(network_one, network_two)

    # return json.dumps(network_one)
    return json.dumps(output)
