import json

from sqlalchemy import and_

from conekt import db
from conekt.models.relationships.sequence_family import SequenceFamilyAssociation


class SequenceSequenceECCAssociation(db.Model):
    __tablename__ = 'sequence_sequence_ecc'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    query_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))
    target_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))

    ecc = db.Column(db.Float)
    p_value = db.Column(db.Float)
    corrected_p_value = db.Column(db.Float)

    gene_family_method_id = db.Column(db.Integer, db.ForeignKey('gene_family_methods.id', ondelete='CASCADE'))
    query_network_method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id', ondelete='CASCADE'))
    target_network_method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id', ondelete='CASCADE'))

    gene_family_method = db.relationship('GeneFamilyMethod', lazy='joined',
                                         backref=db.backref('ecc_as_family_method',
                                                            lazy='dynamic',
                                                            passive_deletes=True)
                                         )

    query_expression_network_method = db.relationship('ExpressionNetworkMethod',
                                                      foreign_keys=[query_network_method_id],
                                                      lazy='joined',
                                                      backref=db.backref('ecc_as_query_method',
                                                                         lazy='dynamic',
                                                                         passive_deletes=True)
                                                      )
    target_expression_network_method = db.relationship('ExpressionNetworkMethod',
                                                       foreign_keys=[target_network_method_id],
                                                       lazy='joined',
                                                       backref=db.backref('ecc_as_target_method',
                                                                          lazy='dynamic',
                                                                          passive_deletes=True)
                                                       )

    @staticmethod
    def get_ecc_network(sequence, network, family):
        """
        Get network connecting a specific sequence to all genes with significant Expression Context Conservation.


        :param sequence: internal ID of sequence
        :param network: network method ID to consider
        :param family: kind of gene families used to detect ECC
        :return: network dict (can be made compatible using CytoscapeHelper)
        """
        data = SequenceSequenceECCAssociation.query.filter(and_(
                SequenceSequenceECCAssociation.query_id == sequence,
                SequenceSequenceECCAssociation.query_network_method_id == network,
                SequenceSequenceECCAssociation.gene_family_method_id == family)).all()

        # return an empty dict in case there are no hits for this query
        if len(data) < 1:
            return {'nodes': [], 'edges': []}

        # add the query node
        d = data[0]
        nodes = [{"id": d.query_sequence.name,
                  "name": d.query_sequence.name,
                  "species_id": d.query_sequence.species_id,
                  "species_name": d.query_sequence.species.name,
                  "gene_id": d.query_id,
                  "gene_name": d.query_sequence.name,
                  "network_method_id": network,
                  "node_type": "query"}]
        edges = []

        networks = {}

        for d in data:
            nodes.append({"id": d.target_sequence.name,
                          "name": d.target_sequence.name,
                          "species_id": d.target_sequence.species_id,
                          "species_name": d.target_sequence.species.name,
                          "gene_id": d.target_id,
                          "network_method_id": d.target_network_method_id,
                          "gene_name": d.target_sequence.name})

            if d.target_network_method_id not in networks.keys():
                networks[d.target_network_method_id] = []
            networks[d.target_network_method_id].append(d.target_id)

            # TODO: add p-value and corrected p once implemented
            edges.append({"source": d.query_sequence.name,
                          "target": d.target_sequence.name,
                          "ecc_score": d.ecc,
                          "edge_type": 0})

        for n, sequences in networks.items():
            new_data = SequenceSequenceECCAssociation.query.filter(and_(
                SequenceSequenceECCAssociation.query_id.in_(sequences),
                SequenceSequenceECCAssociation.target_id.in_(sequences),
                SequenceSequenceECCAssociation.target_network_method_id == n,
                SequenceSequenceECCAssociation.query_network_method_id == n,
                SequenceSequenceECCAssociation.gene_family_method_id == family,
                SequenceSequenceECCAssociation.query_id != SequenceSequenceECCAssociation.target_id
            )).all()

            for nd in new_data:
                # TODO: add p-value and corrected p once implemented
                # make sure the connection doesn't exist already
                if not any(d['source'] == nd.target_sequence.name and d['target'] == nd.query_sequence.name for d in edges):
                    edges.append({"source": nd.query_sequence.name,
                                  "target": nd.target_sequence.name,
                                  "ecc_score": nd.ecc,
                                  "edge_type": 1})

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def get_ecc_pair_network(ecc_id):
        """
        Get all data for an SequenceSequenceECCAssociation to make a ECC graph, similar to the pairwise comparisons in
        Movahedi et al.

        :param ecc_id: interal id of the SequenceSequenceECCAssociation
        :return: ecc pair with neighborhood as graph dict
        """

        association = SequenceSequenceECCAssociation.query.get_or_404(ecc_id)

        nodes = [{"id": association.query_sequence.name,
                  "name": association.query_sequence.name,
                  "species_id": association.query_sequence.species_id,
                  "species_name": association.query_sequence.species.name,
                  "gene_id": association.query_id,
                  "gene_name": association.query_sequence.name,
                  "network_method_id": association.query_network_method_id,
                  "node_type": "query"},
                 {"id": association.target_sequence.name,
                  "name": association.target_sequence.name,
                  "species_id": association.target_sequence.species_id,
                  "species_name": association.target_sequence.species.name,
                  "gene_id": association.target_id,
                  "gene_name": association.target_sequence.name,
                  "network_method_id": association.target_network_method_id,
                  "node_type": "query"},
                 ]

        edges = [{"source": association.query_sequence.name,
                  "target": association.target_sequence.name,
                  "ecc_score": association.ecc,
                  'ecc_pair_color': "#D33",
                  "edge_type": "ecc"}]

        query_network = association.query_sequence.network_nodes.filter_by(method_id=association.query_network_method_id).first_or_404().network
        target_network = association.target_sequence.network_nodes.filter_by(method_id=association.target_network_method_id).first_or_404().network

        query_network_data = json.loads(query_network)
        target_network_data = json.loads(target_network)

        sequences = [association.query_sequence.id, association.target_sequence.id]

        for n in query_network_data:
            gene_id = n['gene_id'] if 'gene_id' in n.keys() else None
            gene_name = n['gene_name'] if 'gene_name' in n.keys() else None

            if gene_id not in sequences:
                nodes.append({
                    "id": gene_name,
                    "name": gene_name,
                    "species_id": association.query_sequence.species_id,
                    "species_name": association.query_sequence.species.name,
                    "gene_id": gene_id,
                    "gene_name": gene_name,
                    "network_method_id": association.query_network_method_id,
                    "node_type": "target"
                })
                sequences.append(gene_id)

            edges.append({"source": association.query_sequence.name,
                          "target": gene_name,
                          "link_score": n['link_score'] if 'link_score' in n else 0,
                          "edge_type": "expression",
                          'ecc_pair_color': "#3D3"})

        for n in target_network_data:
            gene_id = n['gene_id'] if 'gene_id' in n.keys() else None
            gene_name = n['gene_name'] if 'gene_name' in n.keys() else None

            if gene_id not in sequences:
                sequences.append(gene_id)
                nodes.append({
                    "id": gene_name,
                    "name": gene_name,
                    "species_id": association.target_sequence.species_id,
                    "species_name": association.target_sequence.species.name,
                    "gene_id": gene_id,
                    "gene_name": gene_name,
                    "network_method_id": association.target_network_method_id,
                    "node_type": "target"
                })

            edges.append({"source": association.target_sequence.name,
                          "target": gene_name,
                          "link_score": n['link_score'] if 'link_score' in n else 0,
                          "edge_type": "expression",
                          'ecc_pair_color': "#3D3"})

        return {"nodes": nodes, "edges": edges}, association.gene_family_method_id

    @staticmethod
    def get_ecc_multi_network(gf_method_id, sequence_ids):
        """
        Creates an ECC network for multiple genes, the resulting network will contain all ECC partners of the input
        genes. Pruning this network keeping only genes with non-unique label co-occurances is recommended !


        :param gf_method_id: gene family method used to detect ECC
        :param sequence_ids: sequences to include as the core of the network
        :return: network dict
        """
        associations = SequenceSequenceECCAssociation.query.\
            filter(SequenceSequenceECCAssociation.gene_family_method_id == gf_method_id).\
            filter(and_(SequenceSequenceECCAssociation.query_id.in_(sequence_ids),
                        SequenceSequenceECCAssociation.target_id.in_(sequence_ids))).\
            all()

        nodes, edges = [], []
        node_sequence_ids = []

        networks = []

        for a in associations:
            query_network = a.query_sequence.network_nodes.filter_by(
                method_id=a.query_network_method_id).first_or_404().network
            target_network = a.target_sequence.network_nodes.filter_by(
                method_id=a.target_network_method_id).first_or_404().network

            if query_network not in networks:
                networks.append((a.query_id,
                                 a.query_sequence.name,
                                 a.query_sequence.species_id,
                                 a.query_sequence.species.name,
                                 a.query_network_method_id,
                                 query_network))
            if target_network not in networks:
                networks.append((a.target_id,
                                 a.target_sequence.name,
                                 a.target_sequence.species_id,
                                 a.target_sequence.species.name,
                                 a.target_network_method_id,
                                 target_network))

            if a.query_id not in node_sequence_ids:
                node_sequence_ids.append(a.query_id)
                nodes.append({"id": a.query_sequence.name,
                              "name": a.query_sequence.name,
                              "species_id": a.query_sequence.species_id,
                              "species_name": a.query_sequence.species.name,
                              "gene_id": a.query_id,
                              "gene_name": a.query_sequence.name,
                              "network_method_id": a.query_network_method_id,
                              "node_type": "query"})

            if a.target_id not in node_sequence_ids:
                node_sequence_ids.append(a.target_id)
                nodes.append({"id": a.target_sequence.name,
                              "name": a.target_sequence.name,
                              "species_id": a.target_sequence.species_id,
                              "species_name": a.target_sequence.species.name,
                              "gene_id": a.target_id,
                              "gene_name": a.target_sequence.name,
                              "network_method_id": a.target_network_method_id,
                              "node_type": "query"})

            edges.append({"source": a.query_sequence.name,
                          "target": a.target_sequence.name,
                          "ecc_score": a.ecc,
                          'ecc_pair_color': "#D33",
                          "edge_type": "ecc"})

        new_edges = []

        for sequence_id, sequence_name, species_id, species_name, network_method_id, n in networks:
            network_data = json.loads(n)
            for node in network_data:
                gene_id = node['gene_id'] if 'gene_id' in node.keys() else None
                gene_name = node['gene_name'] if 'gene_name' in node.keys() else None

                if gene_id not in node_sequence_ids:
                    node_sequence_ids.append(gene_id)
                    nodes.append({
                        "id": gene_name,
                        "name": gene_name,
                        "species_id": species_id,
                        "species_name": species_name,
                        "gene_id": gene_id,
                        "gene_name": gene_name,
                        "network_method_id": network_method_id,
                        "node_type": "target"
                    })

                if (sequence_name, gene_name) not in new_edges:
                    new_edges.append((sequence_name, gene_name))
                    new_edges.append((gene_name, sequence_name))

                    edges.append({"source": sequence_name,
                                  "target": gene_name,
                                  "link_score": node['link_score'] if 'link_score' in node else 0,
                                  "edge_type": "expression",
                                  'ecc_pair_color': "#3D3"})

        return {"nodes": nodes, "edges": edges}, gf_method_id
