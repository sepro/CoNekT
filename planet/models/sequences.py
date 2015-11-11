from planet import db

from planet.models.relationships import sequence_go, sequence_interpro, sequence_family, sequence_coexpression_cluster
from planet.models.relationships import sequence_xref
from utils.sequence import translate
from config import SQL_COLLATION

class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), index=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    description = db.Column(db.Text)
    coding_sequence = db.deferred(db.Column(db.Text))
    type = db.Column(db.Enum('protein_coding', 'TE', 'RNA', name='sequence_type'), default='protein_coding')
    is_mitochondrial = db.Column(db.Boolean, default=False)
    is_chloroplast = db.Column(db.Boolean, default=False)

    expression_profiles = db.relationship('ExpressionProfile', backref='sequence', lazy='dynamic')
    network_nodes = db.relationship('ExpressionNetwork', backref='sequence', lazy='dynamic')
    interpro_associations = db.relationship('SequenceInterproAssociation', backref='sequence', lazy='dynamic')
    go_associations = db.relationship('SequenceGOAssociation', backref='sequence', lazy='dynamic')
    coexpression_cluster_associations = db.relationship('SequenceCoexpressionClusterAssociation',
                                                        backref=db.backref('sequence', lazy='joined'),
                                                        lazy='dynamic')

    go_labels = db.relationship('GO', secondary=sequence_go, lazy='dynamic')
    interpro_domains = db.relationship('Interpro', secondary=sequence_interpro, lazy='dynamic')
    families = db.relationship('GeneFamily', secondary=sequence_family, lazy='dynamic')
    coexpression_clusters = db.relationship('CoexpressionCluster', secondary=sequence_coexpression_cluster,
                                            lazy='dynamic')

    xrefs = db.relationship('XRef', secondary=sequence_xref, lazy='dynamic')

    def __init__(self, species_id, name, coding_sequence, type='protein_coding', is_chloroplast=False,
                 is_mitochondrial=False):
        self.species_id = species_id
        self.name = name
        self.coding_sequence = coding_sequence
        self.type = type
        self.is_chloroplast = is_chloroplast
        self.is_mitochondrial = is_mitochondrial

    @property
    def protein_sequence(self):
        """
        Function to translate the coding sequence to the amino acid sequence. Will start at the first start codon and
        break after adding a stop codon (indicated by '*')

        :return: The amino acid sequence based on the coding sequence
        """
        return translate(self.coding_sequence)
