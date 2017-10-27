import json

from flask import Blueprint, render_template, g, Response
from sqlalchemy import or_

from conekt import cache
from conekt.helpers.cytoscape import CytoscapeHelper
from conekt.models.expression.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from conekt.models.relationships.cluster_similarity import CoexpressionClusterSimilarity
from conekt.models.relationships.sequence_cluster import SequenceCoexpressionClusterAssociation
from conekt.models.sequences import Sequence
from conekt.models.gene_families import GeneFamilyMethod

from conekt.helpers.chartjs import prepare_avg_profiles

expression_cluster = Blueprint('expression_cluster', __name__)


@expression_cluster.route('/')
def expression_cluster_overview():
    """
    Overview of all networks in the current database with basic information
    """
    cluster_methods = CoexpressionClusteringMethod.query.all()

    return render_template("expression_cluster.html", cluster_methods=cluster_methods, overview=True)


@expression_cluster.route('/view/<cluster_id>')
@cache.cached()
def expression_cluster_view(cluster_id):
    """
    Tablular view of the contents of a single cluster

    :param cluster_id: Internal ID of the cluster
    """
    cluster = CoexpressionCluster.query.get_or_404(cluster_id)

    sequence_count = len(cluster.sequences.with_entities(Sequence.id).all())
    go_enrichment = cluster.go_enrichment.order_by('corrected_p_value').all()
    similar_clusters = CoexpressionClusterSimilarity.query.filter(or_(
        CoexpressionClusterSimilarity.source_id == cluster_id,
        CoexpressionClusterSimilarity.target_id == cluster_id
    )).all()

    return render_template("expression_cluster.html", cluster=cluster,
                           sequence_count=sequence_count,
                           go_enrichment=go_enrichment,
                           similar_clusters=similar_clusters)


@expression_cluster.route('/sequences/<cluster_id>/')
@expression_cluster.route('/sequences/<cluster_id>/<int:page>')
@cache.cached()
def expression_cluster_sequences(cluster_id, page=1):
    """
    Paginated view of the probes (and linked sequences)

    :param cluster_id: Internal ID of the cluster
    :param page: page number
    """
    cluster = CoexpressionCluster.query.get_or_404(cluster_id)
    sequence_associations = cluster.sequence_associations.order_by(SequenceCoexpressionClusterAssociation.probe).paginate(page, g.page_items, False).items

    return render_template('pagination/cluster_probes.html', sequence_associations=sequence_associations,
                           species_id=cluster.method.network_method.species.id)


@expression_cluster.route('/download/<cluster_id>')
def expression_cluster_download(cluster_id):
    """
    Paginated view of the probes (and linked sequences)

    :param cluster_id: Internal ID of the cluster
    :param page: page number
    """
    cluster = CoexpressionCluster.query.get_or_404(cluster_id)
    sequence_associations = cluster.sequence_associations.order_by(SequenceCoexpressionClusterAssociation.probe)

    output = ["\"probe\",\"sequence_id\",\"alias\",\"description\""]

    for sequence_association in sequence_associations:
        line = [sequence_association.probe]
        if sequence_association.sequence is not None:
            line.append(sequence_association.sequence.name)
            aliases = sequence_association.sequence.aliases
            line.append(aliases if aliases is not None else "No alias")
            if sequence_association.sequence.description is not None:
                line.append(sequence_association.sequence.description)
            else:
                line.append("No description available")
        else:
            line.append("None sequence associated with this probe")
            line.append("No alias")
            line.append("No description available")

        output.append('"' + "\",\"".join(line) + '"')

    return Response("\r\n".join(output), mimetype='text/plain')


@expression_cluster.route('/graph/<cluster_id>')
@expression_cluster.route('/graph/<cluster_id>/<int:family_method_id>')
@cache.cached()
def expression_cluster_graph(cluster_id, family_method_id=None):
    """
    Creates the graph with all the members of the cluster

    :param cluster_id: internal identifier of the cluster
    :param family_method_id: gene family method used for color coding the graph
    """
    cluster = CoexpressionCluster.query.get(cluster_id)

    if family_method_id is None:
        family_method = GeneFamilyMethod.query.first()
        if family_method_id is not None:
            family_method_id = family_method.id
        else:
            family_method_id = None

    return render_template("expression_graph.html", cluster=cluster,
                           family_method_id=family_method_id,
                           cutoff=cluster.method.network_method.hrr_cutoff)


@expression_cluster.route('/json/<cluster_id>')
@expression_cluster.route('/json/<cluster_id>/<int:family_method_id>')
@cache.cached()
def expression_cluster_json(cluster_id, family_method_id=None):
    """
    Generates JSON output compatible with cytoscape.js (see planet/static/planet_graph.js for details how to render)

    :param cluster_id: id of the cluster to plot
    :param family_method_id: gene family method used for color coding the graph
    """
    network = CoexpressionCluster.get_cluster(cluster_id)

    if family_method_id is None:
        family_method = GeneFamilyMethod.query.first()
        if family_method is not None:
            family_method_id = family_method.id
        else:
            family_method_id = None

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family_method_id)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_connection_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)

    return Response(json.dumps(network_cytoscape), mimetype='application/json')


@expression_cluster.route('/json/avg_profile/<cluster_id>')
@cache.cached()
def avg_profile(cluster_id):
    current_cluster = CoexpressionCluster.query.get(cluster_id)

    profiles = current_cluster.profiles

    avg_profile = prepare_avg_profiles(profiles, ylabel='TPM (normalized)')

    return Response(json.dumps(avg_profile), mimetype='application/json')


@expression_cluster.route('/tooltip/<cluster_id>')
@cache.cached()
def cluster_tooltip(cluster_id):
    current_cluster = CoexpressionCluster.query.get(cluster_id)

    return render_template('tooltips/cluster.html', cluster=current_cluster)


@expression_cluster.route('/ajax/interpro/<cluster_id>')
@cache.cached()
def cluster_interpro_ajax(cluster_id):
    current_cluster = CoexpressionCluster.query.get(cluster_id)

    return render_template('async/interpro_stats.html',
                           interpro_stats=current_cluster.interpro_stats)


@expression_cluster.route('/ajax/go/<cluster_id>')
@cache.cached()
def cluster_go_ajax(cluster_id):
    current_cluster = CoexpressionCluster.query.get(cluster_id)

    return render_template('async/go_stats.html', go_stats=current_cluster.go_stats)


@expression_cluster.route('/ajax/family/<cluster_id>')
@cache.cached()
def cluster_family_ajax(cluster_id):
    current_cluster = CoexpressionCluster.query.get(cluster_id)

    return render_template('async/family_stats.html', family_stats=current_cluster.family_stats)
