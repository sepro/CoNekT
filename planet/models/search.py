from planet.models.relationships import ClusterGOEnrichment
from planet.models.coexpression_clusters import CoexpressionClusteringMethod


def enriched_clusters_search(go_id, method=-1, min_enrichment=1, max_p=0.05, max_corrected_p=0.00005):
    clusters = ClusterGOEnrichment.query.filter(ClusterGOEnrichment.go_id == go_id)\

    if method != -1:
        clusters = clusters.filter(ClusterGOEnrichment.cluster.has(method_id=method))

    if min_enrichment is not None:
        clusters = clusters.filter(ClusterGOEnrichment.enrichment >= min_enrichment)

    if max_p is not None:
        clusters = clusters.filter(ClusterGOEnrichment.p_value <= max_p)

    if max_corrected_p is not None:
        clusters = clusters.filter(ClusterGOEnrichment.corrected_p_value <= max_corrected_p)

    return clusters.all()

