from flask import Blueprint, url_for, render_template, flash, redirect
from sqlalchemy.sql import and_

from planet.models.expression_networks import ExpressionNetworkMethod, ExpressionNetwork

import json


expression_network = Blueprint('expression_network', __name__)


@expression_network.route('/')
def expression_network_overview():
    """
    Overview of all networks in the current database with basic information
    """
    networks = ExpressionNetworkMethod.query.all()

    return render_template("expression_network.html", networks=networks)


@expression_network.route('/view/<node_id>')
@expression_network.route('/view/<node_id>/<int:depth>')
def expression_network_view(node_id, depth=0):
    """
    Page that displays the network graph for a specific network's probe, the depth indicates how many steps away from
    the query gene the network is retrieved. For performance reasons depths > 2 are not allowed

    :param node_id: id of the network's probe (the query) to visualize
    :param depth: How many steps to include, 0 only the query and the direct neighborhood, 1 a step further, ...
    """
    if depth > 2:
        flash("Depth cannot be larger than 2. Showing the network with depth 2", "warning")
        return redirect(url_for('expression_network.expression_network_view', node_id=node_id, depth=2))

    node = ExpressionNetwork.query.get(node_id)
    return render_template("expression_graph.html", node=node, depth=depth)


@expression_network.route('/json/<node_id>')
@expression_network.route('/json/<node_id>/<int:depth>')
def expression_network_json(node_id, depth=0):
    """
    Generates JSON output compatible with cytoscape.js (see planet/static/planet_graph.js for details how to render)

    :param node_id: id of the network's probe (the query) to visualize
    :param depth: How many steps to include, 0 only the query and the direct neighborhood, 1 a step further, ...
    """
    node = ExpressionNetwork.query.get(node_id)
    links = json.loads(node.network)

    method_id = node.method_id

    # add the initial node
    nodes = [{"data": {"id": node.probe,
                       "name": node.probe,
                       "gene_link": url_for('sequence.sequence_view', sequence_id=node.gene_id),
                       "gene_name": node.gene.name,
                       "node_type": "query",
                       "color": "#888"}}]
    edges = []

    # lists necessary for doing deeper searches
    additional_nodes = []
    existing_edges = []
    existing_nodes = [node.probe]

    # add direct neighbors of the gene of interest

    for link in links:
        nodes.append(__process_link(link))
        edges.append({"data": {"source": node.probe,
                               "target": link["probe_name"],
                               "depth": 0,
                               "link_score": link["link_score"],
                               "color": "#CCC"}})
        additional_nodes.append(link["probe_name"])
        existing_edges.append([node.probe, link["probe_name"]])
        existing_edges.append([link["probe_name"], node.probe])
        existing_nodes.append(link["probe_name"])

    # iterate n times to add deeper links

    for i in range(1, depth+1):
        new_nodes = ExpressionNetwork.query.filter(and_(ExpressionNetwork.probe.in_(additional_nodes),
                                                        ExpressionNetwork.method_id == method_id))
        next_nodes = []

        for new_node in new_nodes:
            new_links = json.loads(new_node.network)

            for link in new_links:
                if link["probe_name"] not in existing_nodes:
                    nodes.append(__process_link(link))
                    existing_nodes.append(link["probe_name"])
                    next_nodes.append(link["probe_name"])

                if [new_node.probe, link["probe_name"]] not in existing_edges:
                    edges.append({"data": {"source": new_node.probe,
                                           "target": link["probe_name"],
                                           "depth": i,
                                           "link_score": link["link_score"],
                                           "color": "#CCC"}})
                    existing_edges.append([new_node.probe, link["probe_name"]])
                    existing_edges.append([link["probe_name"], new_node.probe])

        additional_nodes = next_nodes

    # Add links between the last set of nodes added
    new_nodes = ExpressionNetwork.query.filter(and_(ExpressionNetwork.probe.in_(additional_nodes),
                                                    ExpressionNetwork.method_id == method_id))
    for new_node in new_nodes:
        new_links = json.loads(new_node.network)
        for link in new_links:
            if link["probe_name"] in existing_nodes:
                if [new_node.probe, link["probe_name"]] not in existing_edges:
                    edges.append({"data": {"source": new_node.probe,
                                           "target": link["probe_name"],
                                           "depth": depth+1,
                                           "link_score": link["link_score"],
                                           "color": "#CCC"}})
                    existing_edges.append([new_node.probe, link["probe_name"]])
                    existing_edges.append([link["probe_name"], new_node.probe])

    return json.dumps({"nodes": nodes, "edges": edges})


def __process_link(linked_probe):
    """
    Internal function that processes a linked probe (from the ExpressionNetwork.network field) to a data entry
    compatible with cytoscape.js

    :param linked_probe: hash with information from ExpressionNetwork.network field
    :return: a hash formatted for use as a node with cytoscape.js
    """
    if linked_probe["gene_id"] is not None:
        return {"data": {"id": linked_probe["probe_name"],
                         "name": linked_probe["probe_name"],
                         "gene_link": url_for('sequence.sequence_view', sequence_id=linked_probe["gene_id"]),
                         "gene_name": linked_probe["gene_name"],
                         "node_type": "linked",
                         "color": "#888"}}
    else:
        return {"data": {"id": linked_probe["probe_name"],
                         "name": linked_probe["probe_name"],
                         "gene_link": url_for('sequence.sequence_view', sequence_id=""),
                         "gene_name": linked_probe["gene_name"],
                         "node_type": "linked",
                         "color": "#888"}}


