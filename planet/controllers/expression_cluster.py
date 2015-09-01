from flask import Blueprint, url_for, render_template, flash, redirect

from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.helpers.cytoscape import CytoscapeHelper

import json


expression_cluster = Blueprint('expression_cluster', __name__)


@expression_cluster.route('/')
def expression_cluster_overview():
    """
    Overview of all networks in the current database with basic information
    """
    cluster_methods = CoexpressionClusteringMethod.query.all()

    return render_template("expression_cluster.html", cluster_methods=cluster_methods)


@expression_cluster.route('/graph/<cluster_id>')
def expression_cluster_graph(cluster_id):
    """
    Creates the graph with all the members of the cluster

    :param cluster_id: internal identifier of the cluster
    """
    cluster = CoexpressionCluster.query.get(cluster_id)

    return render_template("expression_graph.html", cluster=cluster)


@expression_cluster.route('/json/<cluster_id>')
def expression_cluster_json(cluster_id):
    """
    Generates JSON output compatible with cytoscape.js (see planet/static/planet_graph.js for details how to render)

    :param cluster_id: id of the cluster to plot
    """
    network = CoexpressionCluster.get_cluster(cluster_id)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, 1)
    network_cytoscape = CytoscapeHelper.add_connection_data_nodes(network_cytoscape)

    return json.dumps(network_cytoscape)
