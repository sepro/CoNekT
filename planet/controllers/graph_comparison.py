from flask import Blueprint, render_template
from planet.models.coexpression_clusters import CoexpressionCluster

from planet.helpers.cytoscape import CytoscapeHelper

import json

graph_comparison = Blueprint('graph_comparison', __name__)


@graph_comparison.route('/')
def graph_comparison_overview():
    return "TEST"


@graph_comparison.route('/cluster/<int:one>/<int:two>')
@graph_comparison.route('/cluster/<int:one>/<int:two>/<int:family_method_id>')
def graph_comparison_cluster(one, two, family_method_id=1):
    cluster_one = CoexpressionCluster.query.get_or_404(one)
    cluster_two = CoexpressionCluster.query.get_or_404(two)

    return render_template('expression_graph.html', cluster_one=cluster_one, cluster_two=cluster_two,
                           family_method_id=family_method_id)


@graph_comparison.route('/cluster/json/<int:one>/<int:two>')
@graph_comparison.route('/cluster/json/<int:one>/<int:two>/<int:family_method_id>')
def graph_comparison_cluster_json(one, two, family_method_id=1):
    # test url http://127.0.0.1:5000/graph_comparison/cluster/1858/2408
    network_one = CytoscapeHelper.parse_network(CoexpressionCluster.get_cluster(one))
    network_one = CytoscapeHelper.add_family_data_nodes(network_one, family_method_id)
    network_one = CytoscapeHelper.add_connection_data_nodes(network_one)

    network_two = CytoscapeHelper.parse_network(CoexpressionCluster.get_cluster(two))
    network_two = CytoscapeHelper.add_family_data_nodes(network_two, family_method_id)
    network_two = CytoscapeHelper.add_connection_data_nodes(network_two)

    output = CytoscapeHelper.merge_networks(network_one, network_two)
    output = CytoscapeHelper.add_lc_data_nodes(output)

    return json.dumps(output)
