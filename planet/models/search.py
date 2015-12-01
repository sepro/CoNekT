from planet.models.relationships import ClusterGOEnrichment


def enriched_clusters_search(go_id, method=-1, min_enrichment=None, max_p=None, max_corrected_p=None):
    """
    Function to get enriched clusters for a specific GO term


    :param go_id: Internal GO id
    :param method: Internal ID of the clustering method (ignored if -1)
    :param min_enrichment: minimal (log2) enrichment score (ignored if None)
    :param max_p: maximum (uncorrected) p-value (ignored if None)
    :param max_corrected_p: maximum corrected p-value (ignored if None)
    :return: all clusters with the desired properties (ignored if None)
    """
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

