from sqlalchemy import func
from sqlalchemy.sql import or_, and_

from planet.models.expression.profiles import ExpressionProfile
from planet.models.gene_families import GeneFamily
from planet.models.go import GO
from planet.models.interpro import Interpro
from planet.models.relationships.cluster_go import ClusterGOEnrichment
from planet.models.sequences import Sequence

import re


class Search:
    @staticmethod
    def simple(term_string):
        """
        Private function to be used internally by the simple search. Performs an intuitive search on various fields.

        all terms are converted into uppercase to make searches case insensitive

        :param term_string: space-separated strings to search for
        :return: dict with results per type
        """
        terms = term_string.upper().split()

        sequences = Sequence.query.filter(or_(or_(*[Sequence.name.ilike(term+"%") for term in terms
                                                    if len(term) > 5]),
                                              Sequence.name.in_(terms),
                                              and_(*[Sequence.description.ilike("%"+term+"%") for term in terms
                                                     if len(term) > 3]),
                                              *[Sequence.xrefs.any(name=term) for term in terms]
                                              )
                                          ).all()

        go = GO.query.filter(or_(and_(*[GO.description.ilike("%"+term+"%") for term in terms]),
                                 and_(*[GO.name.ilike("%"+term+"%") for term in terms]),
                                 GO.label.in_(terms))).all()

        interpro = Interpro.query.filter(or_(and_(*[Interpro.description.ilike("%"+term+"%") for term in terms]),
                                             Interpro.label.in_(terms))).all()

        families = GeneFamily.query.filter(func.upper(GeneFamily.name).in_(terms)).all()
        profiles = ExpressionProfile.query.filter(ExpressionProfile.probe.in_(terms)).all()

        return {"go": go,
                "interpro": interpro,
                "sequences": sequences,
                "families": families,
                "profiles": profiles}

    @staticmethod
    def whooshee_simple(term_string):
        """
        Private function to be used internally by the simple search. Performs an intuitive search on various fields.

        all terms are converted into uppercase to make searches case insensitive

        :param term_string: space-separated strings to search for
        :return: dict with results per type
        """
        terms = term_string.upper().split()

        sequences = Sequence.query.filter(or_(or_(*[Sequence.name.ilike(term+"%") for term in terms
                                                    if len(term) > 5]),
                                              *[Sequence.xrefs.any(name=term) for term in terms]
                                              )
                                          ).all()

        go = GO.query.filter(GO.label.in_(terms)).all()
        interpro = Interpro.query.filter(Interpro.label.in_(terms)).all()

        families = GeneFamily.query.filter(func.upper(GeneFamily.name).in_(terms)).all()
        profiles = ExpressionProfile.query.filter(ExpressionProfile.probe.in_(terms)).all()

        # Whooshee searches
        # First remove non-alphanumerical characters and digits from the string. Split in terms and remove terms
        # that are too short
        whooshee_search_terms = [t for t in re.sub('(\W|\d)+', ' ', term_string).split() if len(t) > 3]
        whooshee_search_string = ' '.join(whooshee_search_terms)

        whooshee_sequences, whooshee_go, whooshee_interpro = [], [], []

        if all([len(t) == 0 for t in [sequences, go, interpro, families, profiles]]) and len(whooshee_search_string) > 3:
            # didn't find a term by ID, try description
            whooshee_go = GO.query.whooshee_search(whooshee_search_string, limit=50).all()
            whooshee_sequences = Sequence.query.whooshee_search(whooshee_search_string, limit=50).all()
            whooshee_interpro = Interpro.query.whooshee_search(whooshee_search_string, limit=50).all()

        return {"go": go + whooshee_go,
                "interpro": interpro + whooshee_interpro,
                "sequences": sequences + whooshee_sequences,
                "families": families,
                "profiles": profiles}

    @staticmethod
    def keyword(keyword):
        """
        Keyword search, this is potentially faster than the simple search

        :param keyword: single word
        :return: dict with results per type
        """
        sequences = Sequence.query.filter(or_(Sequence.name.ilike(keyword+"%"),
                                              Sequence.description.ilike("%"+keyword+"%"),
                                              Sequence.xrefs.any(name=keyword)
                                              )
                                          ).all()

        go = GO.query.filter(or_(GO.description.ilike("%"+keyword+"%"),
                                 GO.name.ilike("%"+keyword+"%"),
                                 GO.label == keyword)).all()

        interpro = Interpro.query.filter(or_(Interpro.description.ilike("%"+keyword+"%"),
                                             Interpro.label == keyword)).all()

        families = GeneFamily.query.filter(GeneFamily.name == keyword).all()
        profiles = ExpressionProfile.query.filter(ExpressionProfile.probe == keyword).all()

        return {"go": go,
                "interpro": interpro,
                "sequences": sequences,
                "families": families,
                "profiles": profiles}

    @staticmethod
    def enriched_clusters(go_id, method=-1, min_enrichment=None, max_p=None, max_corrected_p=None):
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

