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

    networks= {}

    for d in data:
        nodes.append({"id": d.target_id,
                      "name": d.target_sequence.name,
                      "species_id": d.target_sequence.species_id,
                      "gene_id": d.target_id,
                      "network_method_id": d.target_network_method_id,
                      "gene_name": d.target_sequence.name})

        if d.target_network_method_id not in networks.keys():
            networks[d.target_network_method_id] = []
        networks[d.target_network_method_id].append(d.target_id)

        # TODO: add p-value and corrected p once implemented
        edges.append({"source": sequence.id,
                      "target": d.target_id,
                      "ecc_score": d.ecc,
                      "edge_type": 'ecc_prime'})

    # TODO add next level of connectivity
    for n, sequences in networks.items():
        new_data = SequenceSequenceECCAssociation.query.filter(and_(
            SequenceSequenceECCAssociation.query_id.in_(sequences),
            SequenceSequenceECCAssociation.target_network_method_id == n,
            SequenceSequenceECCAssociation.query_network_method_id == n,
            SequenceSequenceECCAssociation.gene_family_method_id == family,
            SequenceSequenceECCAssociation.query_id != SequenceSequenceECCAssociation.target_id
        )).all()

        for nd in new_data:
            # TODO: add p-value and corrected p once implemented
            # make sure the connection doesn't exist already
            if not any(d['source'] == nd.target_id and d['target'] == nd.query_id for d in edges):
                edges.append({"source": nd.query_id,
                              "target": nd.target_id,
                              "ecc_score": nd.ecc,
                              "edge_type": 'ecc_secondary'})

    network = {"nodes": nodes, "edges": edges}

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_species_data_nodes(network_cytoscape)

    return json.dumps(network_cytoscape)
