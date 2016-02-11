from flask import Blueprint, redirect, url_for, render_template
from sqlalchemy import and_

from planet.models.sequences import Sequence
from planet.models.relationships import SequenceSequenceECCAssociation

from planet.helpers.cytoscape import CytoscapeHelper

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
    sequence = Sequence.query.get_or_404(sequence)
    return render_template("expression_graph.html",
                           sequence=sequence,
                           network_method_id=network,
                           family_method_id=family)


@ecc.route('/json/<int:sequence>/<int:network>/<int:family>')
def ecc_graph_json(sequence, network, family):

    network = SequenceSequenceECCAssociation.get_ecc_network(sequence, network, family)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_species_data_nodes(network_cytoscape)

    return json.dumps(network_cytoscape)
