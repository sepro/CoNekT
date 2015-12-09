from flask import Blueprint, url_for, render_template, flash, redirect, g, Response

from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.helpers.cytoscape import CytoscapeHelper

from planet.models.sequences import Sequence

import json


expression_cluster = Blueprint('expression_cluster', __name__)


@expression_cluster.route('/')
def expression_cluster_overview():
    """
    Overview of all networks in the current database with basic information
    """
    cluster_methods = CoexpressionClusteringMethod.query.all()

    return render_template("expression_cluster.html", cluster_methods=cluster_methods)


@expression_cluster.route('/view/<cluster_id>')
def expression_cluster_view(cluster_id):
    """
    Tablular view of the contents of a single cluster

    :param cluster_id: Internal ID of the cluster
    """
    cluster = CoexpressionCluster.query.get_or_404(cluster_id)

    sequence_count = len(cluster.sequences.with_entities(Sequence.id).all())
    go_enrichment = cluster.go_enrichment.order_by('corrected_p_value').all()

    return render_template("expression_cluster.html", cluster=cluster,
                           sequence_count=sequence_count,
                           go_enrichment=go_enrichment)


@expression_cluster.route('/sequences/<cluster_id>/')
@expression_cluster.route('/sequences/<cluster_id>/<int:page>')
def expression_cluster_sequences(cluster_id, page=1):
    """
    Paginated view of the probes (and linked sequences)

    :param cluster_id: Internal ID of the cluster
    :param page: page number
    """
    cluster = CoexpressionCluster.query.get_or_404(cluster_id)
    sequence_associations = cluster.sequence_associations.order_by('probe').paginate(page, g.page_items, False).items

    return render_template('pagination/cluster_probes.html', sequence_associations=sequence_associations,
                           species_id=cluster.method.network_method.species.id)


@expression_cluster.route('/download/<cluster_id>/')
def expression_cluster_download(cluster_id):
    """
    Paginated view of the probes (and linked sequences)

    :param cluster_id: Internal ID of the cluster
    :param page: page number
    """
    cluster = CoexpressionCluster.query.get_or_404(cluster_id)
    sequence_associations = cluster.sequence_associations.order_by('probe')

    output = ["probe\tsequence"]

    for sequence_association in sequence_associations:
        if sequence_association.sequence is not None:
            output.append(sequence_association.probe + "\t" + sequence_association.sequence.name)
        else:
            output.append(sequence_association.probe + "\tNone")

    return Response("\n".join(output), mimetype='text/plain')


@expression_cluster.route('/graph/<cluster_id>')
@expression_cluster.route('/graph/<cluster_id>/<int:family_method_id>')
def expression_cluster_graph(cluster_id, family_method_id=1):
    """
    Creates the graph with all the members of the cluster

    :param cluster_id: internal identifier of the cluster
    """
    cluster = CoexpressionCluster.query.get(cluster_id)

    return render_template("expression_graph.html", cluster=cluster, family_method_id=family_method_id)


@expression_cluster.route('/json/<cluster_id>')
@expression_cluster.route('/json/<cluster_id>/<int:family_method_id>')
def expression_cluster_json(cluster_id, family_method_id=1):
    """
    Generates JSON output compatible with cytoscape.js (see planet/static/planet_graph.js for details how to render)

    :param cluster_id: id of the cluster to plot
    """
    network = CoexpressionCluster.get_cluster(cluster_id)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family_method_id)
    network_cytoscape = CytoscapeHelper.add_connection_data_nodes(network_cytoscape)

    return json.dumps(network_cytoscape)
