from flask import Blueprint, redirect, url_for
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


@ecc.route('/json/<int:sequence>/<int:network>/<int:family>')
def ecc_graph_json(sequence, network, family):
    # TODO: refactor ! getting the network should be property of relation or sequence!
    sequence = Sequence.query.get_or_404(sequence)
    data = sequence.ecc_query_associations.filter(and_(
            SequenceSequenceECCAssociation.query_network_method_id == network,
            SequenceSequenceECCAssociation.gene_family_method_id == family)).all()

    # add the initial node
    nodes = [{"id": sequence.id,
              "name": sequence.name,
              "species_id": sequence.species_id,
              "gene_id": sequence.id,
              "gene_name": sequence.name,
              "network_method_id": network,
              "node_type": "query"}]
    edges = []

    for d in data:
        nodes.append({"id": d.target_id,
                      "name": d.target_sequence.name,
                      "species_id": d.target_sequence.species_id,
                      "gene_id": d.target_id,
                      "network_method_id": d.target_network_method_id,
                      "gene_name": d.target_sequence.name})

        # TODO: add p-value and corrected p once implemented
        edges.append({"source": sequence.name,
                      "target": d.target_sequence.name,
                      "ecc_score": d.ecc})

    # TODO add next level of connectivity

    network = {"nodes": nodes, "edges": edges}

    cytoscape_network = CytoscapeHelper.parse_network(network)

    return json.dumps(cytoscape_network)
