from flask import Blueprint, redirect, url_for, render_template, Response

from planet.models.expression_networks import ExpressionNetworkMethod, ExpressionNetwork

import json

expression_network = Blueprint('expression_network', __name__)

@expression_network.route('/')
def expression_network_overview():
    networks = ExpressionNetworkMethod.query.all()

    return render_template("expression_network.html", networks=networks)


@expression_network.route('/json/<node_id>')
def expression_network_json(node_id):
    node = ExpressionNetwork.query.get(node_id)
    links = json.loads(node.network)

    nodes = [{"data": {"id": node.probe, "name": node.probe}}]
    edges = []

    for link in links:
        nodes.append({"data": {"id": link["probe_name"], "name": link["probe_name"]}})
        edges.append({"data": {"source": node.probe, "target": link["probe_name"]}})

    return json.dumps({"nodes": nodes, "edges": edges})


@expression_network.route('/view/<node_id>')
def expression_network_view(node_id):
    node = ExpressionNetwork.query.get(node_id)
    return render_template("expression_graph.html", node=node)
