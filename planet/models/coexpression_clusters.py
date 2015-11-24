from flask import url_for

from planet import db
from planet.models.expression_networks import ExpressionNetwork
from planet.models.relationships import sequence_coexpression_cluster, SequenceGOAssociation, ClusterGOEnrichment

from utils.enrichment import hypergeo_sf, fdr_correction
from utils.benchmark import benchmark

from sqlalchemy.orm import joinedload, load_only

import json
from math import log2


class CoexpressionClusteringMethod(db.Model):
    __tablename__ = 'coexpression_clustering_methods'
    id = db.Column(db.Integer, primary_key=True)
    network_method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'), index=True)
    method = db.Column(db.Text)
    cluster_count = db.Column(db.Integer)

    clusters = db.relationship('CoexpressionCluster', backref=db.backref('method', lazy='joined'), lazy='dynamic')

    def calculate_enrichment(self):
        gene_count = self.network_method.species.sequence_count
        species_id = self.network_method.species_id

        clusters = self.clusters.all()

        for cluster in clusters:
            print(gene_count, species_id, cluster.id)
            pass

    @staticmethod
    def update_counts():
        """
        To avoid long counts the number of clusters per method can be precalculated and stored in the database
        using this function
        """
        methods = CoexpressionClusteringMethod.query.all()

        for m in methods:
            m.cluster_count = m.clusters.count()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)


class CoexpressionCluster(db.Model):
    __tablename__ = 'coexpression_clusters'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('coexpression_clustering_methods.id'))
    name = db.Column(db.String(50), index=True)

    sequences = db.relationship('Sequence', secondary=sequence_coexpression_cluster, lazy='dynamic')
    sequence_associations = db.relationship('SequenceCoexpressionClusterAssociation',
                                            backref=db.backref('coexpression_cluster', lazy='joined'),
                                            lazy='dynamic')

    go_enrichment = db.relationship('ClusterGOEnrichment',
                                    backref=db.backref('cluster', lazy='joined'),
                                    lazy='dynamic')

    @staticmethod
    def get_cluster(cluster_id):
        """
        Returns the network for a whole cluster (reporting edges only between members of the cluster !)

        :param cluster_id: internal ID of the cluster
        """
        cluster = CoexpressionCluster.query.get(cluster_id)

        probes = [member.probe for member in cluster.sequence_associations.all()]

        network = cluster.method.network_method.probes.\
            options(joinedload('sequence').load_only('name')).\
            filter(ExpressionNetwork.probe.in_(probes)).all()

        nodes = []
        edges = []

        existing_edges = []

        for node in network:
            nodes.append({"id": node.probe,
                          "name": node.probe,
                          "gene_id": int(node.sequence_id) if node.sequence_id is not None else None,
                          "gene_name": node.sequence.name if node.sequence_id is not None else node.probe,
                          "depth": 0})

            links = json.loads(node.network)

            for link in links:
                # only add links that are in the cluster !
                if link["probe_name"] in probes and [node.probe, link["probe_name"]] not in existing_edges:
                    edges.append({"source": node.probe,
                                  "target": link["probe_name"],
                                  "profile_comparison":
                                      url_for('expression_profile.expression_profile_compare_probes',
                                              probe_a=node.probe,
                                              probe_b=link["probe_name"],
                                              species_id=node.method.species.id),
                                  "depth": 0,
                                  "link_score": link["link_score"],
                                  "edge_type": cluster.method.network_method.edge_type})
                    existing_edges.append([node.probe, link["probe_name"]])
                    existing_edges.append([link["probe_name"], node.probe])

        return {"nodes": nodes, "edges": edges}

    def __calculate_enrichment(self):
        """
        Initial implementation to calculate GO enrichment for a single cluster
        """
        gene_count = self.method.network_method.species.sequence_count
        species_id = self.method.network_method.species_id

        sequences = self.sequences.options(load_only("id")).all()

        associations = SequenceGOAssociation.query\
            .filter(SequenceGOAssociation.sequence_id.in_([s.id for s in sequences]))\
            .options(load_only("sequence_id", "go_id"))\
            .group_by(SequenceGOAssociation.sequence_id, SequenceGOAssociation.go_id)

        go_data = {}

        for a in associations:
            if a.go_id not in go_data.keys():
                go_data[a.go_id] = {}
                go_data[a.go_id]["total_count"] = json.loads(a.go.species_counts)[str(species_id)]
                go_data[a.go_id]["cluster_count"] = 1
            else:
                go_data[a.go_id]["cluster_count"] += 1

        p_values = []
        for go_id in go_data:
            p_values.append(hypergeo_sf(go_data[go_id]['cluster_count'],
                                        len(sequences),
                                        go_data[go_id]['total_count'],
                                        gene_count))

        corrected_p_values = fdr_correction(p_values)

        for i, go_id in enumerate(go_data):
            enrichment = ClusterGOEnrichment()
            enrichment.cluster_id = self.id
            enrichment.go_id = go_id

            enrichment.cluster_count = go_data[go_id]['cluster_count']
            enrichment.cluster_size = len(sequences)
            enrichment.go_count = go_data[go_id]['total_count']
            enrichment.go_size = gene_count

            enrichment.enrichment = log2((go_data[go_id]['cluster_count']/len(sequences))/(go_data[go_id]['total_count']/gene_count))
            enrichment.p_value = p_values[i]
            enrichment.corrected_p_value = corrected_p_values[i]

            db.session.add(enrichment)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @staticmethod
    def calculate_enrichment(empty=True):
        """
        Static method to calculate the enrichment for all cluster in the database

        :param empty: empty table cluster_go_enrichment first
        :return:
        """
        # If required empty the table first
        if empty:
            try:
                db.session.query(ClusterGOEnrichment).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
            else:
                clusters = CoexpressionCluster.query.all()

                for i, cluster in enumerate(clusters):
                    print(i, "\t cluster: ", cluster.method_id, cluster.name)
                    cluster.__calculate_enrichment()
