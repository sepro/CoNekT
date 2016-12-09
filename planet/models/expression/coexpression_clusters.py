import json
from math import log2

from flask import url_for
from sqlalchemy import join
from sqlalchemy.orm import joinedload, load_only

from planet import db
from planet.models.expression.networks import ExpressionNetwork
from planet.models.gene_families import GeneFamily
from planet.models.relationships import CoexpressionClusterSimilarity, SequenceCoexpressionClusterAssociation, SequenceFamilyAssociation
from planet.models.relationships import SequenceGOAssociation, ClusterGOEnrichment
from planet.models.sequences import Sequence
from utils.benchmark import benchmark
from utils.enrichment import hypergeo_sf, fdr_correction
from utils.jaccard import jaccard


class CoexpressionClusteringMethod(db.Model):
    __tablename__ = 'coexpression_clustering_methods'
    id = db.Column(db.Integer, primary_key=True)
    network_method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'), index=True)
    method = db.Column(db.Text)
    cluster_count = db.Column(db.Integer)

    clusters = db.relationship('CoexpressionCluster',
                               backref=db.backref('method', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

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

    @staticmethod
    def add_lstrap_coexpression_clusters(cluster_file, description, network_id, prefix='cluster_', min_size=10):
        # get all sequences from the database and create a dictionary
        sequences = Sequence.query.all()

        sequence_dict = {}
        for member in sequences:
            sequence_dict[member.name.upper()] = member

        # add coexpression clustering method to the database
        clustering_method = CoexpressionClusteringMethod()

        clustering_method.network_method_id = network_id
        clustering_method.method = description

        try:
            db.session.add(clustering_method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            quit()

        with open(cluster_file) as f:
            i = 1
            for line in f:
                probes = [p for p in line.strip().split()]
                genes = [p.replace('.1', '') for p in probes]
                cluster_id = "%s%04d" % (prefix, i)

                if len(probes) >= min_size:
                    i += 1

                    new_cluster = CoexpressionCluster()
                    new_cluster.method_id = clustering_method.id
                    new_cluster.name = cluster_id

                    db.session.add(new_cluster)

                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(e)
                        continue

                    for p, g in zip(probes, genes):
                        new_association = SequenceCoexpressionClusterAssociation()
                        new_association.probe = p
                        new_association.sequence_id = None
                        if g.upper() in sequence_dict.keys():
                            new_association.sequence_id = sequence_dict[g.upper()].id
                        new_association.coexpression_cluster_id = new_cluster.id
                        db.session.add(new_association)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(e)

        return clustering_method.id


class CoexpressionCluster(db.Model):
    __tablename__ = 'coexpression_clusters'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('coexpression_clustering_methods.id'))
    name = db.Column(db.String(50), index=True)

    # sequences = db.relationship('Sequence', secondary=sequence_coexpression_cluster, lazy='dynamic')

    # Other properties
    # sequences defined in Sequence
    # sequence_associations defined in SequenceCoexpressionClusterAssociation'

    go_enrichment = db.relationship('ClusterGOEnrichment',
                                    backref=db.backref('cluster', lazy='joined'),
                                    lazy='dynamic')

    @staticmethod
    def get_cluster(cluster_id):
        """
        Returns the network for a whole cluster (reporting edges only between members of the cluster !)

        :param cluster_id: internal ID of the cluster
        :return network for the selected cluster (dict with nodes and edges)
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
                                  "link_pcc": link["link_pcc"] if "link_pcc" in link.keys() else None,
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
                    # print(i, "\t cluster: ", cluster.method_id, cluster.name)
                    cluster.__calculate_enrichment()

    @staticmethod
    @benchmark
    def calculate_similarities(gene_family_method_id=1, percentile_pass=0.95):
        """
        This function will calculate ALL similarities between clusters in the database. Results will be added to the
        DB

        :param gene_family_method_id: Internal ID of gene family method to use to calculate the scores (default = 1)
        :param percentile_pass: percentile based cutoff (default = 0.95)
        """

        # sqlalchemy to fetch cluster associations
        fields = [SequenceCoexpressionClusterAssociation.__table__.c.sequence_id,
                  SequenceCoexpressionClusterAssociation.__table__.c.coexpression_cluster_id]
        condition = SequenceCoexpressionClusterAssociation.__table__.c.sequence_id is not None
        cluster_associations = db.engine.execute(db.select(fields).where(condition)).fetchall()

        # sqlalchemy to fetch sequence family associations
        fields = [SequenceFamilyAssociation.__table__.c.sequence_id, SequenceFamilyAssociation.__table__.c.gene_family_id, GeneFamily.__table__.c.method_id]
        condition = GeneFamily.__table__.c.method_id == gene_family_method_id
        table = join(SequenceFamilyAssociation.__table__, GeneFamily.__table__, SequenceFamilyAssociation.__table__.c.gene_family_id == GeneFamily.__table__.c.id)
        sequence_families = db.engine.execute(db.select(fields).select_from(table).where(condition)).fetchall()

        # convert sqlachemy results into dictionary
        sequence_to_family = {seq_id: fam_id for seq_id, fam_id, method_id in sequence_families}

        cluster_to_sequences = {}
        cluster_to_families = {}

        for seq_id, cluster_id in cluster_associations:
            if cluster_id not in cluster_to_sequences.keys():
                cluster_to_sequences[cluster_id] = []
            cluster_to_sequences[cluster_id].append(seq_id)

        for cluster_id, sequences in cluster_to_sequences.items():
            families = list(set([sequence_to_family[s] for s in sequences if s in sequence_to_family.keys()]))
            if len(families) > 0:
                cluster_to_families[cluster_id] = families

        keys = list(cluster_to_families.keys())

        data = []

        for i in range(len(keys) - 1):
            for j in range(i+1, len(keys)):
                current_keys = [keys[x] for x in [i, j]]
                current_families = [cluster_to_families[k] for k in current_keys]

                if len(current_families[0]) > 4 and len(current_families[1]) > 4:
                    j = jaccard(current_families[0], current_families[1])
                    data.append([current_keys[0], current_keys[1], j])

        ordered_j = sorted([a[2] for a in data])
        percentile_cutoff = ordered_j[int(len(ordered_j)*percentile_pass)]

        database = [{'source_id': d[0],
                     'target_id': d[1],
                     'gene_family_method_id': gene_family_method_id,
                     'jaccard_index': d[2],
                     'p_value': 0,
                     'corrected_p_value': 0} for d in data if d[2] >= percentile_cutoff]

        db.engine.execute(CoexpressionClusterSimilarity.__table__.insert(), database)
