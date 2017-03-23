import json
from math import log2
from collections import defaultdict

from flask import url_for
from sqlalchemy import join
from sqlalchemy.orm import joinedload, load_only

from planet import db
from planet.models.expression.networks import ExpressionNetwork, ExpressionNetworkMethod
from planet.models.gene_families import GeneFamily
from planet.models.interpro import Interpro
from planet.models.go import GO
from planet.models.relationships.cluster_similarity import CoexpressionClusterSimilarity
from planet.models.relationships.sequence_cluster import SequenceCoexpressionClusterAssociation
from planet.models.relationships.sequence_family import SequenceFamilyAssociation
from planet.models.relationships.sequence_go import SequenceGOAssociation
from planet.models.relationships.cluster_go import ClusterGOEnrichment
from planet.models.sequences import Sequence

from utils.benchmark import benchmark
from utils.enrichment import hypergeo_sf, fdr_correction
from utils.jaccard import jaccard
from utils.hcca import HCCA


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
    def clusters_from_neighborhoods(method, network_method_id):
        probes = ExpressionNetwork.query.filter_by(method_id=network_method_id).all()  # Load all probes

        clusters = defaultdict(list)
        clusters_orm = {}

        for p in probes:
            # Only consider probes linked with sequences
            if p.sequence_id is not None:
                neighborhood = json.loads(p.network)
                sequence_ids = [n["gene_id"] for n in neighborhood if "gene_id" in n.keys()
                                and n["gene_id"] is not None]

                # check if there are neighbors for this sequence
                if len(sequence_ids) > 0:
                    clusters[p.sequence.name] = [p.sequence_id] + sequence_ids

        # If there are valid clusters add them to the database
        if len(clusters) > 0:

            # Add new method first
            new_method = CoexpressionClusteringMethod()

            new_method.network_method_id = network_method_id
            new_method.method = method
            new_method.cluster_count = len(clusters)

            db.session.add(new_method)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

        # Add Clusters
        for cluster, members in clusters.items():
            clusters_orm[cluster] = CoexpressionCluster()
            clusters_orm[cluster].method_id = new_method.id
            clusters_orm[cluster].name = cluster
            db.session.add(clusters_orm[cluster])

            if len(clusters_orm) % 400 == 0:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(e)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

        # Add sequence cluster relations

    @staticmethod
    def build_hcca_clusters(method, network_method_id, step_size=3, hrr_cutoff=30, min_cluster_size=40, max_cluster_size=200):
        """
        method to build HCCA clusters for a certain network

        :param method: Name for the current clustering method
        :param network_method_id: ID for the network to cluster
        :param step_size: desired step_size for the HCCA algorithm
        :param hrr_cutoff: desired hrr_cutoff for the HCCA algorithm
        :param min_cluster_size: minimal cluster size
        :param max_cluster_size: maximum cluster size
        """

        network_data = {}

        sequence_probe = {}

        # Get network from DB
        print("Loading Network data from DB...", sep='')
        ExpressionNetworkMethod.query.get_or_404(network_method_id)                     # Check if method exists

        probes = ExpressionNetwork.query.filter_by(method_id=network_method_id).all()   # Load all probes

        for p in probes:
            # Loop over probes and store hrr for all neighbors
            if p.sequence_id is not None:
                neighborhood = json.loads(p.network)
                network_data[p.sequence_id] = {nb["gene_id"]: nb["hrr"] for nb in neighborhood
                                               if "gene_id" in nb.keys()
                                               and "hrr" in nb.keys()
                                               and nb["gene_id"] is not None}

                sequence_probe[p.sequence_id] = p.probe

        # Double check edges are reciprocally defined
        for sequence, data in network_data.items():
            for neighbor, score in data.items():
                if neighbor not in network_data.keys():
                    network_data[neighbor] = {sequence: score}
                else:
                    if sequence not in network_data[neighbor].keys():
                        network_data[neighbor][sequence] = score

        print("Done!\nStarting to build Clusters...\n")

        # Build clusters
        hcca_util = HCCA(
            step_size=step_size,
            hrr_cutoff=hrr_cutoff,
            min_cluster_size=min_cluster_size,
            max_cluster_size=max_cluster_size
        )

        hcca_util.load_data(network_data)

        hcca_util.build_clusters()

        # Add new method to DB
        clusters = list(set([t[1] for t in hcca_util.clusters]))
        if len(clusters) > 0:
            print("Done building clusters, adding clusters to DB")

            # Add new method first
            new_method = CoexpressionClusteringMethod()

            new_method.network_method_id = network_method_id
            new_method.method = method
            new_method.cluster_count = len(clusters)

            db.session.add(new_method)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

            # Add cluster and store as dict
            cluster_dict = {}

            for c in clusters:
                cluster_dict[c] = CoexpressionCluster()
                cluster_dict[c].method_id = new_method.id
                cluster_dict[c].name = c

                db.session.add(cluster_dict[c])

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

            # Link sequences to clusters
            for i, t in enumerate(hcca_util.clusters):
                gene_id, cluster_name, _ = t

                relation = SequenceCoexpressionClusterAssociation()

                relation.probe = sequence_probe[gene_id] if gene_id in sequence_probe.keys() else None
                relation.sequence_id = gene_id
                relation.coexpression_cluster_id = cluster_dict[cluster_name].id if cluster_name in cluster_dict.keys() else None

                if relation.coexpression_cluster_id is not None:
                    db.session.add(relation)

                if i > 0 and i % 400 == 0:
                    # Add relations in sets of 400
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(e)

            # Add remaining relations
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)


        else:
            print("No clusters found! Not adding anything to DB !")

    @staticmethod
    def add_lstrap_coexpression_clusters(cluster_file, description, network_id, prefix='cluster_', min_size=10):
        """
        Adds MCL clusters, as produced by LSTrAP, to the database

        :param cluster_file: path to file with clusters
        :param description: description to add to database for this set of clusters
        :param network_id: network the clusters are based on
        :param prefix: prefix for individual clsuter names (default 'cluster_')
        :param min_size: minimal size of a cluster (default = 10)
        :return: ID of new clustering method
        """
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
    # go_enrichment defined in ClusterGOEnrichment


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
    def delete_enrichment():
        """
        Removes all GO enrichment data from the database

        :return:
        """
        try:
            db.session.query(ClusterGOEnrichment).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

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
        if len(ordered_j) > 0:
            percentile_cutoff = ordered_j[int(len(ordered_j)*percentile_pass)]

            database = [{'source_id': d[0],
                         'target_id': d[1],
                         'gene_family_method_id': gene_family_method_id,
                         'jaccard_index': d[2],
                         'p_value': 0,
                         'corrected_p_value': 0} for d in data if d[2] >= percentile_cutoff]

            db.engine.execute(CoexpressionClusterSimilarity.__table__.insert(), database)
        else:
            print("No similar clusters found!")

    @property
    def interpro_stats(self):
        sequence_ids = [s.id for s in self.sequences.all()]

        return Interpro.sequence_stats(sequence_ids)

    @property
    def go_stats(self):
        sequence_ids = [s.id for s in self.sequences.all()]

        return GO.sequence_stats(sequence_ids)

    @property
    def family_stats(self):
        sequence_ids = [s.id for s in self.sequences.all()]

        return GeneFamily.sequence_stats(sequence_ids)
