import json

from flask import Blueprint, url_for, render_template, flash, redirect, Response

from conekt import cache
from conekt.helpers.cytoscape import CytoscapeHelper
from conekt.models.expression.networks import ExpressionNetworkMethod, ExpressionNetwork
from conekt.models.species import Species
from conekt.models.gene_families import GeneFamilyMethod

from utils.benchmark import benchmark

expression_network = Blueprint('expression_network', __name__)


@expression_network.route('/')
def expression_network_overview():
    """
    Overview of all networks in the current database with basic information
    """
    networks = ExpressionNetworkMethod.query.all()

    return render_template("expression_network.html", networks=networks)


@expression_network.route('/species/<species_id>')
@cache.cached()
def expression_network_species(species_id):
    """
    Overview of all networks in the current database with basic information
    """
    networks = ExpressionNetworkMethod.query.filter_by(species_id=species_id).all()
    species = Species.query.get_or_404(species_id)

    return render_template("expression_network.html", networks=networks, species=species)


@expression_network.route('/graph/<node_id>')
@expression_network.route('/graph/<node_id>/<int:family_method_id>')
@cache.cached()
def expression_network_graph(node_id, family_method_id=None):
    """
    Page that displays the network graph for a specific network's probe, the depth indicates how many steps away from
    the query gene the network is retrieved. For performance reasons depths > 1 are not allowed

    :param node_id: id of the network's probe (the query) to visualize
    :param depth: How many steps to include, 0 only the query and the direct neighborhood, 1 a step further, ...
    Currently unused, filtering is done by javascript downstream
    :param family_method_id: family method to use for colors and shapes based on the family
    """
    if family_method_id is None:
        family_method = GeneFamilyMethod.query.first()
        if family_method is not None:
            family_method_id = family_method.id
        else:
            family_method_id = None

    node = ExpressionNetwork.query.get(node_id)
    enable_second_level = node.method.enable_second_level

    depth = 1 if enable_second_level else 0

    return render_template("expression_graph.html", node=node, depth=depth, family_method_id=family_method_id,
                           cutoff=node.method.hrr_cutoff)


@expression_network.route('/download/neighbors/<node_id>')
@cache.cached()
def expression_network_download_neighbors(node_id):
    """
    Returns tab delimited table with neighbors of the current node

    :param node_id:
    :return: Response with table in tab delimited format
    """

    network = ExpressionNetwork.query.get(node_id)

    return Response(network.neighbors_table)


@expression_network.route('/json/<node_id>')
@expression_network.route('/json/<node_id>/<int:family_method_id>')
@cache.cached()
def expression_network_json(node_id, family_method_id=None):
    """
    Generates JSON output compatible with cytoscape.js (see planet/static/planet_graph.js for details how to render)

    :param node_id: id of the network's probe (the query) to visualize
    :param family_method_id: Which gene families to use
    """

    node = ExpressionNetwork.query.get(node_id)
    enable_second_level = node.method.enable_second_level
    depth = 1 if enable_second_level else 0

    network = ExpressionNetwork.get_neighborhood(node_id, depth=depth)

    if family_method_id is None:
        family_method = GeneFamilyMethod.query.first()
        if family_method is not None:
            family_method_id = family_method.id
        else:
            family_method_id = None

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family_method_id)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)

    return Response(json.dumps(network_cytoscape), mimetype='application/json')


@expression_network.route('/export/<method_id>')
def expression_network_export(method_id):

    def generate(method_id):
        header = "gene_a\tgene_b\thrr\tpcc\n"
        yield header

        nodes = ExpressionNetwork.query.filter(ExpressionNetwork.method_id == method_id).all()

        for n in nodes:
            neighbors = json.loads(n.network)
            for neighbor in neighbors:
                gene_a = n.sequence.name if n.sequence_id is not None else n.probe

                probe_b = neighbor["probe_name"] if "probe_name" in neighbor.keys() else "Unknown"
                gene_b = neighbor["gene_name"] if "gene_name" in neighbor.keys() else probe_b

                hrr = neighbor["hrr"] if "hrr" in neighbor.keys() else None
                pcc = neighbor["link_pcc"] if "link_pcc" in neighbor.keys() else None

                yield '\t'.join([gene_a, gene_b, str(hrr), str(pcc)]) + '\n'

    return Response(generate(method_id), mimetype='text/plain')

