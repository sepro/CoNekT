from sqlalchemy import func
from sqlalchemy.sql import or_, and_

from conekt.models.expression.profiles import ExpressionProfile
from conekt.models.gene_families import GeneFamily
from conekt.models.go import GO
from conekt.models.interpro import Interpro
from conekt.models.expression.coexpression_clusters import CoexpressionCluster
from conekt.models.relationships.cluster_go import ClusterGOEnrichment
from conekt.models.relationships.cluster_clade import ClusterCladeEnrichment
from conekt.models.sequences import Sequence
from conekt.models.xrefs import XRef
from conekt.models.species import Species

import re
import whoosh


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
                                          ).limit(50).all()

        go = GO.query.filter(or_(and_(*[GO.description.ilike("%"+term+"%") for term in terms]),
                                 and_(*[GO.name.ilike("%"+term+"%") for term in terms]),
                                 GO.label.in_(terms))).limit(50).all()

        interpro = Interpro.query.filter(or_(and_(*[Interpro.description.ilike("%"+term+"%") for term in terms]),
                                             Interpro.label.in_(terms))).limit(50).all()

        families = GeneFamily.query.filter(func.upper(GeneFamily.name).in_(terms)).limit(50).all()
        profiles = ExpressionProfile.query.filter(ExpressionProfile.probe.in_(terms)).limit(50).all()

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
        terms = [t for t in term_string.upper().split() if len(t) > 3]

        sequences_by_name = Sequence.query.filter(Sequence.name.in_(terms)).limit(50).all()

        sequences_by_xref = Sequence.query.filter(Sequence.xrefs.any(XRef.name.in_(terms))).limit(50).all()

        sequences = sequences_by_name + sequences_by_xref

        go = GO.query.filter(GO.label.in_(terms)).all()
        interpro = Interpro.query.filter(Interpro.label.in_(terms)).all()

        families = GeneFamily.query.filter(func.upper(GeneFamily.name).in_(terms)).limit(50).all()
        profiles = ExpressionProfile.query.filter(ExpressionProfile.probe.in_(terms)).limit(50).all()

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

        return {"go": (go + whooshee_go)[:50],
                "interpro": (interpro + whooshee_interpro)[:50],
                "sequences": (sequences + whooshee_sequences)[:50],
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
                                          ).limit(50).all()

        go = GO.query.filter(or_(GO.description.ilike("%"+keyword+"%"),
                                 GO.name.ilike("%"+keyword+"%"),
                                 GO.label == keyword)).limit(50).all()

        interpro = Interpro.query.filter(or_(Interpro.description.ilike("%"+keyword+"%"),
                                             Interpro.label == keyword)).limit(50).all()

        families = GeneFamily.query.filter(GeneFamily.name == keyword).limit(50).all()
        profiles = ExpressionProfile.query.filter(ExpressionProfile.probe == keyword).limit(50).all()

        return {"go": go,
                "interpro": interpro,
                "sequences": sequences,
                "families": families,
                "profiles": profiles}

    @staticmethod
    def advanced_sequence_search(species_id, gene_list, terms, term_rules, gene_family_method_id, gene_families,
                                 go_terms, go_rules, interpro_domains,
                                 interpro_rules, include_predictions=False):
        valid_species_ids = [s.id for s in Species.query.all()]

        query = Sequence.query

        if gene_family_method_id > 0:
            query = query.filter(Sequence.families.any(or_(*[
                and_(GeneFamily.method_id == gene_family_method_id, GeneFamily.name == name) for name in gene_families])))

        # Add species filter if necessary
        if species_id is not None and species_id in valid_species_ids:
            query = query.filter(Sequence.species_id == species_id)

        if len(gene_list) > 0:
            query = query.filter(or_(*[or_(Sequence.name == gene,
                                           Sequence.xrefs.any(name=gene)) for gene in gene_list]))

        # Add terms filter if necessary
        if len(terms.strip()) > 5:
            if term_rules == 'exact':
                # EXACT MATCH
                query = query.filter(Sequence.description.ilike("%" + terms + "%"))
            else:
                # Prepare whooshee search (remove short strings)
                whooshee_search_terms = [t for t in re.sub('(\W|\d)+', ' ', terms).split() if len(t) > 3]
                whooshee_search_string = ' '.join(whooshee_search_terms)
                if len(whooshee_search_string) > 5:
                    if term_rules == 'all':
                        # AND logic
                        query = query.whooshee_search(whooshee_search_string, group=whoosh.qparser.AndGroup, limit=200)
                    else:
                        # OR logic
                        query = query.whooshee_search(whooshee_search_string, group=whoosh.qparser.OrGroup, limit=200)

        # Filter for GO terms
        if go_terms is not None and len(go_terms) > 0:
            selected_go_id = [go.id for go in GO.query.filter(GO.name.in_(go_terms)).all()]

            if go_rules == 'all':
                if include_predictions:
                    query = query.filter(and_(*[Sequence.go_associations.any(go_id=go_id) for go_id in selected_go_id]))
                else:
                    query = query.filter(and_(*[Sequence.go_associations.any(go_id=go_id, predicted=0)
                                                for go_id in selected_go_id]))
            else:
                if include_predictions:
                    query = query.filter(or_(*[Sequence.go_associations.any(go_id=go_id) for go_id in selected_go_id]))
                else:
                    query = query.filter(or_(*[Sequence.go_associations.any(go_id=go_id, predicted=0)
                                               for go_id in selected_go_id]))

        # Filter for InterPro domains
        if interpro_domains is not None and len(interpro_domains) > 0:
            if interpro_rules == 'all':
                query = query.filter(and_(*[Sequence.interpro_domains.any(description=t) for t in interpro_domains]))
            else:
                query = query.filter(or_(*[Sequence.interpro_domains.any(description=t) for t in interpro_domains]))

        sequences = query.limit(200).all()

        return sequences

    @staticmethod
    def count_enriched_clusters(go_id, method=-1, min_enrichment=None, max_p=None, max_corrected_p=None,
                                enriched_clade_id=None):
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

        if enriched_clade_id is not None:
            clusters = clusters.filter(ClusterGOEnrichment.cluster.has(
                CoexpressionCluster.clade_enrichment.any(clade_id=enriched_clade_id)))

        return clusters.count()

    @staticmethod
    def enriched_clusters(go_id, method=-1, min_enrichment=None, max_p=None, max_corrected_p=None,
                          enriched_clade_id=None):
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

        if enriched_clade_id is not None:
            clusters = clusters.filter(ClusterGOEnrichment.cluster.has(
                CoexpressionCluster.clade_enrichment.any(clade_id=enriched_clade_id)))

        return clusters.all()

