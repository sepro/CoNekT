from flask import Blueprint, url_for, render_template, flash, redirect

from planet.models.expression_networks import ExpressionNetworkMethod, ExpressionNetwork
from planet.helpers.cytoscape import CytoscapeHelper

import json


expression_network = Blueprint('expression_network', __name__)


@expression_network.route('/')
def expression_network_overview():
    """
    Overview of all networks in the current database with basic information
    """
    networks = ExpressionNetworkMethod.query.all()

    return render_template("expression_network.html", networks=networks)


@expression_network.route('/species/<species_id>')
def expression_network_species(species_id):
    """
    Overview of all networks in the current database with basic information
    """
    networks = ExpressionNetworkMethod.query.filter_by(species_id=species_id).all()

    return render_template("expression_network.html", networks=networks)


@expression_network.route('/graph/<node_id>/')
def expression_network_graph(node_id, depth=1):
    """
    Page that displays the network graph for a specific network's probe, the depth indicates how many steps away from
    the query gene the network is retrieved. For performance reasons depths > 2 are not allowed

    :param node_id: id of the network's probe (the query) to visualize
    :param depth: How many steps to include, 0 only the query and the direct neighborhood, 1 a step further, ...
    """
    if depth > 1:
        flash("Depth cannot be larger than 2. Showing the network with depth 1", "warning")
        return redirect(url_for('expression_network.expression_network_graph', node_id=node_id, depth=2))

    node = ExpressionNetwork.query.get(node_id)

    return render_template("expression_graph.html", node=node, depth=depth)


@expression_network.route('/json/<node_id>')
@expression_network.route('/json/<node_id>/<int:depth>')
def expression_network_json(node_id, depth=1):
    """
    Generates JSON output compatible with cytoscape.js (see planet/static/planet_graph.js for details how to render)

    :param node_id: id of the network's probe (the query) to visualize
    :param depth: How many steps to include, 0 only the query and the direct neighborhood, 1 a step further, ...
    """
    network = ExpressionNetwork.get_neighborhood(node_id, depth)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, 1)
    network_cytoscape = CytoscapeHelper.add_depth_data_edges(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_depth_data_nodes(network_cytoscape)

    return json.dumps(network_cytoscape)


