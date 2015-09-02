from sqlalchemy import and_

from planet import db

import json


class ExpressionNetworkMethod(db.Model):
    __tablename__ = 'expression_network_methods'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    description = db.Column(db.Text)
    edge_type = db.Column(db.Enum("rank", "weight", name='edge_type'))

    probes = db.relationship('ExpressionNetwork', backref='method', lazy='dynamic')

    clustering_methods = db.relationship('CoexpressionClusteringMethod', backref='network_method', lazy='dynamic')

    def __init__(self, species_id, description, edge_type="rank"):
        self.species_id = species_id
        self.description = description
        self.edge_type = edge_type


class ExpressionNetwork(db.Model):
    __tablename__ = 'expression_networks'
    id = db.Column(db.Integer, primary_key=True)
    probe = db.Column(db.String(50))
    sequence_id = db.Column(db.String(50), db.ForeignKey('sequences.id'))
    network = db.Column(db.Text)
    method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'))

    def __init__(self, probe, sequence_id, network, method_id):
        self.probe = probe
        self.sequence_id = sequence_id
        self.network = network
        self.method_id = method_id

    @staticmethod
    def get_neighborhood(probe, depth=0):
        node = ExpressionNetwork.query.get(probe)
        links = json.loads(node.network)

        method_id = node.method_id
        edge_type = node.method.edge_type

        # add the initial node
        nodes = [{"id": node.probe,
                  "name": node.probe,
                  "gene_id": int(node.sequence_id) if node.sequence_id is not None else None,
                  "gene_name": node.gene.name if node.sequence_id is not None else node.probe,
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
                          "depth": 0,
                          "link_score": link["link_score"],
                          "edge_type": edge_type})
            additional_nodes.append(link["probe_name"])
            existing_edges.append([node.probe, link["probe_name"]])
            existing_edges.append([link["probe_name"], node.probe])
            existing_nodes.append(link["probe_name"])

        # iterate n times to add deeper links

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
                                      "depth": i,
                                      "link_score": link["link_score"],
                                      "edge_type": edge_type})
                        existing_edges.append([new_node.probe, link["probe_name"]])
                        existing_edges.append([link["probe_name"], new_node.probe])

            additional_nodes = next_nodes

        # Add links between the last set of nodes added
        new_nodes = ExpressionNetwork.query.filter(and_(ExpressionNetwork.probe.in_(additional_nodes),
                                                        ExpressionNetwork.method_id == method_id))
        for new_node in new_nodes:
            new_links = json.loads(new_node.network)
            for link in new_links:
                if link["probe_name"] in existing_nodes:
                    if [new_node.probe, link["probe_name"]] not in existing_edges:
                        edges.append({"source": new_node.probe,
                                      "target": link["probe_name"],
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
