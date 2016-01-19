from flask import url_for
from config import SQL_COLLATION
from planet import db
from planet.models.relationships import SequenceFamilyAssociation
from planet.models.gene_families import GeneFamily

from utils.jaccard import jaccard
from utils.benchmark import benchmark

import json
from sqlalchemy import and_


class ExpressionNetworkMethod(db.Model):
    __tablename__ = 'expression_network_methods'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), index=True)
    description = db.Column(db.Text)
    edge_type = db.Column(db.Enum("rank", "weight", name='edge_type'))
    probe_count = db.Column(db.Integer)

    probes = db.relationship('ExpressionNetwork', backref=db.backref('method', lazy='joined'), lazy='dynamic')

    clustering_methods = db.relationship('CoexpressionClusteringMethod', backref='network_method', lazy='dynamic')

    def __init__(self, species_id, description, edge_type="rank"):
        self.species_id = species_id
        self.description = description
        self.edge_type = edge_type

    def __repr__(self):
        return str(self.id) + ". " + self.description

    @staticmethod
    def update_count():
        """
        To avoid long count queries the number of networks for each method can be precalculated and stored in the
        database using this function
        """
        methods = ExpressionNetworkMethod.query.all()

        for m in methods:
            m.probe_count = m.probes.count()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @staticmethod
    @benchmark
    def calculate_ecc(network_method_ids, gene_family_method_id):
        """
        Function to calculate the ECC scores in and between genes of different networks

        ORM free method for speed !

        :param network_method_ids: array of networks (using their internal id !) to compare
        :param gene_family_method_id: internal id of the type of family methods to be used for the comparison
        """

        sequence_network = {}
        sequence_family = {}
        family_sequence = {}

        # Get all the network information and store in dictionary
        for n in network_method_ids:
            print(n)
            current_network = db.engine.execute(db.select([ExpressionNetwork.__table__.c.sequence_id,
                                                       ExpressionNetwork.__table__.c.network]).
                                                   where(ExpressionNetwork.__table__.c.method_id == n).
                                                   where(ExpressionNetwork.__table__.c.sequence_id != None)
                                                ).fetchall()

            for sequence, network in current_network:
                sequence_network[int(sequence)] = network

        # Get family data and store in dictionary
        current_families = db.engine.execute(db.select([SequenceFamilyAssociation.__table__.c.sequence_id,
                                                        SequenceFamilyAssociation.__table__.c.gene_family_id,
                                                        GeneFamily.__table__.c.method_id]).
                                             select_from(SequenceFamilyAssociation.__table__.join(GeneFamily.__table__)).
                                             where(GeneFamily.__table__.c.method_id == gene_family_method_id)
                                             ).fetchall()

        for sequence, family, method in current_families:
            sequence_family[int(sequence)] = int(family)

            if family not in family_sequence.keys():
                family_sequence[int(family)] = []

            family_sequence[int(family)].append(int(sequence))

        # Data loaded start calculating ECCs
        for family, sequences in family_sequence.items():
            for query in sequences:
                for target in sequences:
                    if query in sequence_network.keys() and target in sequence_network.keys() and query != target:
                        ecc = ExpressionNetworkMethod.__ecc(sequence_network[query],
                                                            sequence_network[target],
                                                            sequence_family)
                        print(target, query, ecc)

    @staticmethod
    def __ecc(q_network, t_network, families):
        q_data = json.loads(q_network)
        t_data = json.loads(t_network)

        q_genes = [t['gene_id'] for t in q_data if t['gene_id'] is not None]
        t_genes = [t['gene_id'] for t in t_data if t['gene_id'] is not None]

        q_families = [families[q] for q in q_genes if q in families.keys()]
        t_families = [families[t] for t in t_genes if t in families.keys()]

        if len(q_families) == 0 or len(t_families) == 0:
            return 0.0
        else:
            return jaccard(q_families, t_families)


class ExpressionNetwork(db.Model):
    __tablename__ = 'expression_networks'
    id = db.Column(db.Integer, primary_key=True)
    probe = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'), index=True)
    network = db.Column(db.Text)
    method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'), index=True)

    def __init__(self, probe, sequence_id, network, method_id):
        self.probe = probe
        self.sequence_id = sequence_id
        self.network = network
        self.method_id = method_id

    @staticmethod
    def get_neighborhood(probe, depth=0):
        """
        Get the coexpression neighborhood for a specific probe

        :param probe: internal ID of the probe
        :param depth: how many steps away from the query you wish to expand the network
        :return: dict with nodes and edges
        """
        node = ExpressionNetwork.query.get(probe)
        links = json.loads(node.network)

        method_id = node.method_id
        edge_type = node.method.edge_type

        # add the initial node
        nodes = [{"id": node.probe,
                  "name": node.probe,
                  "probe_id": node.id,
                  "gene_id": int(node.sequence_id) if node.sequence_id is not None else None,
                  "gene_name": node.sequence.name if node.sequence_id is not None else node.probe,
                  "node_type": "query",
                  "depth": 0}]
        edges = []

        # lists necessary for doing deeper searches
        additional_nodes = []
        existing_edges = []
        existing_nodes = [node.probe]

        # add direct neighbors of the gene of interest

        for link in links:
            nodes.append(ExpressionNetwork.__process_link(link, depth=0))
            edges.append({"source": node.probe,
                          "target": link["probe_name"],
                          "profile_comparison":
                              url_for('expression_profile.expression_profile_compare_probes',
                                      probe_a=node.probe,
                                      probe_b=link["probe_name"],
                                      species_id=node.method.species.id),
                          "depth": 0,
                          "link_score": link["link_score"],
                          "edge_type": edge_type})
            additional_nodes.append(link["probe_name"])
            existing_edges.append([node.probe, link["probe_name"]])
            existing_edges.append([link["probe_name"], node.probe])
            existing_nodes.append(link["probe_name"])

        # iterate n times to add deeper links
        if len(additional_nodes) > 0:
            for i in range(1, depth+1):
                new_nodes = ExpressionNetwork.\
                    query.filter(and_(ExpressionNetwork.probe.in_(additional_nodes),
                                      ExpressionNetwork.method_id == method_id))
                next_nodes = []

                for new_node in new_nodes:
                    new_links = json.loads(new_node.network)

                    for link in new_links:
                        if link["probe_name"] not in existing_nodes:
                            nodes.append(ExpressionNetwork.__process_link(link, depth=depth))
                            existing_nodes.append(link["probe_name"])
                            next_nodes.append(link["probe_name"])

                        if [new_node.probe, link["probe_name"]] not in existing_edges:
                            edges.append({"source": new_node.probe,
                                          "target": link["probe_name"],
                                          "profile_comparison":
                                              url_for('expression_profile.expression_profile_compare_probes',
                                                      probe_a=new_node.probe,
                                                      probe_b=link["probe_name"],
                                                      species_id=node.method.species.id),
                                          "depth": i,
                                          "link_score": link["link_score"],
                                          "edge_type": edge_type})
                            existing_edges.append([new_node.probe, link["probe_name"]])
                            existing_edges.append([link["probe_name"], new_node.probe])

                additional_nodes = next_nodes

        # Add links between the last set of nodes added
        new_nodes = []
        if len(additional_nodes) > 0:
            new_nodes = ExpressionNetwork.query.filter(and_(ExpressionNetwork.probe.in_(additional_nodes),
                                                            ExpressionNetwork.method_id == method_id))

        for new_node in new_nodes:
            new_links = json.loads(new_node.network)
            for link in new_links:
                if link["probe_name"] in existing_nodes:
                    if [new_node.probe, link["probe_name"]] not in existing_edges:
                        edges.append({"source": new_node.probe,
                                      "target": link["probe_name"],
                                      "profile_comparison":
                                          url_for('expression_profile.expression_profile_compare_probes',
                                                  probe_a=new_node.probe,
                                                  probe_b=link["probe_name"],
                                                  species_id=node.method.species.id),
                                      "depth": depth+1,
                                      "link_score": link["link_score"],
                                      "edge_type": edge_type})
                        existing_edges.append([new_node.probe, link["probe_name"]])
                        existing_edges.append([link["probe_name"], new_node.probe])

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def __process_link(linked_probe, depth):
        """
        Internal function that processes a linked probe (from the ExpressionNetwork.network field) to a data entry
        compatible with cytoscape.js

        :param linked_probe: hash with information from ExpressionNetwork.network field
        :return: a hash formatted for use as a node with cytoscape.js
        """
        if linked_probe["gene_id"] is not None:
            return {"id": linked_probe["probe_name"],
                    "name": linked_probe["probe_name"],
                    "gene_id": linked_probe["gene_id"],
                    "gene_name": linked_probe["gene_name"],
                    "node_type": "linked",
                    "depth": depth}
        else:
            return {"id": linked_probe["probe_name"],
                    "name": linked_probe["probe_name"],
                    "gene_id": None,
                    "gene_name": linked_probe["probe_name"],
                    "node_type": "linked",
                    "depth": depth}

    @staticmethod
    def calculate_enrichment():
        # first get all GO info
        # for each probe get neighborhood and calculate
        pass