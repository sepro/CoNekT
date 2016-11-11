import json

from planet import db

from sqlalchemy import and_

sequence_go = db.Table('sequence_go',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                       db.Column('go_id', db.Integer, db.ForeignKey('go.id'), index=True)
                       )

sequence_interpro = db.Table('sequence_interpro',
                             db.Column('id', db.Integer, primary_key=True),
                             db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                             db.Column('interpro_id', db.Integer, db.ForeignKey('interpro.id'), index=True),
                             )

sequence_family = db.Table('sequence_family',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                           db.Column('gene_family_id', db.Integer, db.ForeignKey('gene_families.id'), index=True)
                           )

sequence_coexpression_cluster = \
    db.Table('sequence_coexpression_cluster',
             db.Column('id', db.Integer, primary_key=True),
             db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
             db.Column('coexpression_cluster_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True)
             )

coexpression_cluster_similarity = \
    db.Table('coexpression_cluster_similarity',
             db.Column('id', db.Integer, primary_key=True),
             db.Column('source_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True),
             db.Column('target_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True)
             )

sequence_xref = db.Table('sequence_xref',
                         db.Column('id', db.Integer, primary_key=True),
                         db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                         db.Column('xref_id', db.Integer, db.ForeignKey('xrefs.id'), index=True)
                         )

sequence_sequence_ecc = db.Table('sequence_sequence_ecc',
                                 db.Column('id', db.Integer, primary_key=True),
                                 db.Column('query_id', db.Integer, db.ForeignKey('sequences.id'), index=True),
                                 db.Column('target_id', db.Integer, db.ForeignKey('sequences.id'), index=True)
                                 )

family_xref = db.Table('family_xref',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('gene_family_id', db.Integer, db.ForeignKey('gene_families.id'), index=True),
                       db.Column('xref_id', db.Integer, db.ForeignKey('xrefs.id'), index=True)
                       )

cluster_go_enrichment = db.Table('cluster_go_enrichment',
                                 db.Column('id', db.Integer, primary_key=True),
                                 db.Column('cluster_id', db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True),
                                 db.Column('go_id', db.Integer, db.ForeignKey('go.id'), index=True)
                                 )


class SequenceCoexpressionClusterAssociation(db.Model):
    __tablename__ = 'sequence_coexpression_cluster'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    probe = db.Column(db.String(50), index=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    coexpression_cluster_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))

    sequence = db.relationship('Sequence', backref=db.backref('coexpression_cluster_associations',
                                                              lazy='dynamic',
                                                              cascade="all, delete-orphan"),
                               lazy='joined')
    coexpression_cluster = db.relationship('CoexpressionCluster',
                                           backref=db.backref('sequence_associations',
                                                              lazy='dynamic',
                                                              cascade="all, delete-orphan"),
                                           lazy='joined')


class CoexpressionClusterSimilarity(db.Model):
    __tablename__ = 'coexpression_cluster_similarity'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))

    gene_family_method_id = db.Column('gene_family_method_id', db.Integer, db.ForeignKey('gene_family_methods.id'),
                                      index=True)

    jaccard_index = db.Column(db.Float, index=True)
    p_value = db.Column(db.Float, index=True)
    corrected_p_value = db.Column(db.Float, index=True)

    source = db.relationship('CoexpressionCluster', lazy='joined', foreign_keys=[source_id])
    target = db.relationship('CoexpressionCluster', lazy='joined', foreign_keys=[target_id])

    gene_family_method = db.relationship('GeneFamilyMethod', lazy='joined')


class SequenceFamilyAssociation(db.Model):
    __tablename__ = 'sequence_family'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    gene_family_id = db.Column(db.Integer, db.ForeignKey('gene_families.id'))

    sequence = db.relationship('Sequence', lazy='joined')
    family = db.relationship('GeneFamily', lazy='joined')


class SequenceInterproAssociation(db.Model):
    __tablename__ = 'sequence_interpro'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    interpro_id = db.Column(db.Integer, db.ForeignKey('interpro.id'))
    start = db.Column(db.Integer, default=None)
    stop = db.Column(db.Integer, default=None)

    sequence = db.relationship('Sequence', backref=db.backref('interpro_associations',
                                                              lazy='dynamic',
                                                              cascade='all, delete-orphan'))

    domain = db.relationship('Interpro', lazy='select')


class SequenceGOAssociation(db.Model):
    __tablename__ = 'sequence_go'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    go_id = db.Column(db.Integer, db.ForeignKey('go.id'))

    evidence = db.Column(db.Enum('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP',
                                 'ISS', 'ISO', 'ISA', 'ISM', 'IGC', 'IBA', 'IBD', 'IKR', 'IRD', 'RCA',
                                 'TAS', 'NAS', 'IC', 'ND', 'IEA', name='evidence'))
    source = db.Column(db.Text)

    sequence = db.relationship('Sequence', backref=db.backref('go_associations',
                                                              lazy='dynamic',
                                                              cascade='all, delete-orphan'), lazy='joined')

    go = db.relationship('GO', backref=db.backref('sequence_associations',
                                                  lazy='dynamic',
                                                  cascade='all, delete-orphan'), lazy='joined')


class SequenceSequenceECCAssociation(db.Model):
    __tablename__ = 'sequence_sequence_ecc'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    query_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))

    ecc = db.Column(db.Float)
    p_value = db.Column(db.Float)
    corrected_p_value = db.Column(db.Float)

    gene_family_method_id = db.Column(db.Integer, db.ForeignKey('gene_family_methods.id'))
    query_network_method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'))
    target_network_method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'))

    gene_family_method = db.relationship('GeneFamilyMethod', lazy='joined')
    query_expression_network_method = db.relationship('ExpressionNetworkMethod',
                                                      foreign_keys=[query_network_method_id],
                                                      lazy='joined')
    target_expression_network_method = db.relationship('ExpressionNetworkMethod',
                                                       foreign_keys=[target_network_method_id],
                                                       lazy='joined')

    @staticmethod
    def get_ecc_network(sequence, network, family):
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
        Get all data for an SequenceSequenceECCAssociation to make a ECC graph


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
                  "edge_type": 1}]

        query_network = association.query_sequence.network_nodes.filter_by(method_id=association.query_network_method_id).first_or_404().network
        target_network = association.target_sequence.network_nodes.filter_by(method_id=association.target_network_method_id).first_or_404().network

        query_network_data = json.loads(query_network)
        target_network_data = json.loads(target_network)

        # print(query_network_data)

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
                          "link_score": n['link_score'] if 'link_score' in n else 0})

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
                          "link_score": n['link_score'] if 'link_score' in n else 0})

        """
        Add gene families to sequences
        """
        seq_fams = SequenceFamilyAssociation.query.filter(and_(SequenceFamilyAssociation.sequence_id.in_(sequences),
                                                                 SequenceFamilyAssociation.family.has(method_id=association.gene_family_method_id)
                                                                 )).all()

        seq_to_fam = {sf.sequence_id: sf.gene_family_id for sf in seq_fams}

        for i, node in enumerate(nodes):
            nodes[i]['family_id'] = seq_to_fam[node['gene_id']] if node['gene_id'] in seq_to_fam.keys() else None

        """
        Add edges between homologous genes from different targets
        """

        for i in range(len(nodes) - 1):
            for j in range(i + 1, len(nodes)):
                if nodes[i]['family_id'] == nodes[j]['family_id'] and nodes[i]['family_id'] is not None:
                    edges.append(
                        {'source': nodes[i]['id'],
                         'target': nodes[j]['id'],
                         'color': "#33D",
                         'homology': True}
                    )

        return {"nodes": nodes, "edges": edges}, association.gene_family_method_id


class ClusterGOEnrichment(db.Model):
    __tablename__ = 'cluster_go_enrichment'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))
    go_id = db.Column(db.Integer, db.ForeignKey('go.id'))

    """
    Counts required to calculate the enrichment,
    store here for quick access
    """
    cluster_count = db.Column(db.Integer)
    cluster_size = db.Column(db.Integer)
    go_count = db.Column(db.Integer)
    go_size = db.Column(db.Integer)

    """
    Enrichment score (log-transformed), p-value and corrected p-value. Calculated using the hypergeometric
    distribution and applying FDR correction (aka. BH)
    """
    enrichment = db.Column(db.Float)
    p_value = db.Column(db.Float)
    corrected_p_value = db.Column(db.Float)

    @property
    def cluster_percentage(self):
        return self.cluster_count*100/self.cluster_size

    @property
    def genome_percentage(self):
        return self.go_count*100/self.go_size
