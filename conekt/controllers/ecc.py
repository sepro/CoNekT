from flask import Blueprint, redirect, url_for, render_template
from sqlalchemy import and_

from conekt.models.sequences import Sequence
from conekt.models.relationships.sequence_sequence_ecc import SequenceSequenceECCAssociation

from conekt.helpers.cytoscape import CytoscapeHelper

import json

ecc = Blueprint('ecc', __name__)


@ecc.route('/')
def ecc_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@ecc.route('/graph/<int:sequence>/<int:network>/<int:family>')
def ecc_graph(sequence, network, family):
    """
    Returns a page rendering the ECC graph for a specific sequence

    :param sequence: Internal ID of a sequence
    :param network: Internal ID of the network method
    :param family: Internal ID of the family method
    :return: Response with html page that shows the ECC network
    """
    sequence = Sequence.query.get_or_404(sequence)
    return render_template("expression_graph.html",
                           sequence=sequence,
                           network_method_id=network,
                           family_method_id=family)


@ecc.route('/graph_multi/')
def ecc_graph_multi():
    """
    Returns a page rendering the ECC graph for a specific pair of sequences

    :param ecc_id: internal ID of the sequence to sequence ECC relationship
    :return: Response with html page that shows the pairwise ECC network
    """

    return render_template("expression_graph.html",
                           ecc_multi=True)


@ecc.route('/graph_pair/<int:ecc_id>')
def ecc_graph_pair(ecc_id):
    """
    Returns a page rendering the ECC graph for a specific pair of sequences

    :param ecc_id: internal ID of the sequence to sequence ECC relationship
    :return: Response with html page that shows the pairwise ECC network
    """
    ecc_pair = SequenceSequenceECCAssociation.query.get_or_404(ecc_id)

    return render_template("expression_graph.html",
                           ecc_pair=ecc_pair)


@ecc.route('/json/<int:sequence>/<int:network>/<int:family>')
def ecc_graph_json(sequence, network, family):
    """
    Returns a JSON object compatible with cytoscape.js that contains the ECC graph for a specific sequence

    :param sequence: Internal ID of a sequence
    :param network: Internal ID of the network method
    :param family: Internal ID of the family method
    :return: JSON object compatible with cytoscape.js
    """

    network = SequenceSequenceECCAssociation.get_ecc_network(sequence, network, family)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_species_data_nodes(network_cytoscape)

    return json.dumps(network_cytoscape)


@ecc.route('/pair_json/<int:ecc_id>')
def ecc_graph_pair_json(ecc_id):
    """
    Returns a JSON object compatible with cytoscape.js that contains the ECC graph for a specific pair of sequences

    :param ecc_id: internal ID of the sequence to sequence ECC relationship
    :return: JSON object compatible with cytoscape.js
    """
    network, family = SequenceSequenceECCAssociation.get_ecc_pair_network(ecc_id)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_species_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.connect_homologs(network_cytoscape)
    network_cytoscape = CytoscapeHelper.tag_ecc_singles(network_cytoscape)

    return json.dumps(network_cytoscape)


@ecc.route('/multi_json/')
def ecc_graph_multi_json():
    """
    Returns a JSON object compatible with cytoscape.js that contains the ECC graph for a specific pair of sequences

    :param ecc_id: internal ID of the sequence to sequence ECC relationship
    :return: JSON object compatible with cytoscape.js
    """
    network, family = SequenceSequenceECCAssociation.get_ecc_multi_network(1, [162930, 56261, 203621, 94050])

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_species_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.connect_homologs(network_cytoscape)
    network_cytoscape = CytoscapeHelper.tag_ecc_singles(network_cytoscape)

    return json.dumps(network_cytoscape)
