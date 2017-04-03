from planet import db, whooshee

from planet.models.relationships import sequence_go, sequence_interpro, sequence_family, sequence_coexpression_cluster
from planet.models.relationships import sequence_xref, sequence_sequence_ecc
from utils.sequence import translate
from utils.parser.fasta import Fasta

from sqlalchemy.orm import undefer
import operator

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


@whooshee.register_model('description')
class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE'), index=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    description = db.Column(db.Text)
    coding_sequence = db.deferred(db.Column(db.Text))
    type = db.Column(db.Enum('protein_coding', 'TE', 'RNA', name='sequence_type'), default='protein_coding')
    is_mitochondrial = db.Column(db.Boolean, default=False)
    is_chloroplast = db.Column(db.Boolean, default=False)

    expression_profiles = db.relationship('ExpressionProfile', backref=db.backref('sequence', lazy='joined'),
                                          lazy='dynamic',
                                          cascade="all, delete-orphan",
                                          passive_deletes=True)
    network_nodes = db.relationship('ExpressionNetwork',
                                    backref='sequence',
                                    lazy='dynamic',
                                    cascade="all, delete-orphan",
                                    passive_deletes=True)

    # Other properties
    #
    # coexpression_cluster_associations declared in 'SequenceCoexpressionClusterAssociation'
    # interpro_associations declared in 'SequenceInterproAssociation'
    # go_associations declared in 'SequenceGOAssociation'
    # family_associations declared in 'SequenceFamilyAssociation'

    go_labels = db.relationship('GO', secondary=sequence_go, lazy='dynamic')
    interpro_domains = db.relationship('Interpro', secondary=sequence_interpro, lazy='dynamic')
    families = db.relationship('GeneFamily', secondary=sequence_family, lazy='dynamic')

    coexpression_clusters = db.relationship('CoexpressionCluster', secondary=sequence_coexpression_cluster,
                                            backref=db.backref('sequences', lazy='dynamic'),
                                            lazy='dynamic')

    ecc_query_associations = db.relationship('SequenceSequenceECCAssociation',
                                             primaryjoin="SequenceSequenceECCAssociation.query_id == Sequence.id",
                                             backref=db.backref('query_sequence', lazy='joined'),
                                             lazy='dynamic')

    ecc_target_associations = db.relationship('SequenceSequenceECCAssociation',
                                              primaryjoin="SequenceSequenceECCAssociation.target_id == Sequence.id",
                                              backref=db.backref('target_sequence', lazy='joined'),
                                              lazy='dynamic')

    xrefs = db.relationship('XRef', secondary=sequence_xref, lazy='joined')

    def __init__(self, species_id, name, coding_sequence, type='protein_coding', is_chloroplast=False,
                 is_mitochondrial=False, description=None):
        self.species_id = species_id
        self.name = name
        self.description = description
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

    @property
    def aliases(self):
        """
        Returns a readable string with the aliases or tokens stored for this sequence in the table xrefs

        :return: human readable string with aliases or None
        """
        t = [x.name for x in self.xrefs if x.platform == 'token']

        return ", ".join(t) if len(t) > 0 else None

    @property
    def readable_type(self):
        """
        Converts the type table to a readable string

        :return: string with readable version of the sequence type
        """
        conversion = {'protein_coding': 'protein coding',
                      'TE': 'transposable element',
                      'RNA': 'RNA'}

        if self.type in conversion.keys():
            return conversion[self.type]
        else:
            return 'other'

    @staticmethod
    def add_from_fasta(filename, species_id, compressed=False):
        fasta_data = Fasta()
        fasta_data.readfile(filename, compressed=compressed)

        new_sequences = []

        # Loop over sequences, sorted by name (key here) and add to db
        for name, sequence in sorted(fasta_data.sequences.items(), key=operator.itemgetter(0)):
            new_sequence = {"species_id": species_id,
                            "name": name,
                            "description": None,
                            "coding_sequence": sequence,
                            "type": "protein_coding",
                            "is_mitochondrial": False,
                            "is_chloroplast": False}

            new_sequences.append(new_sequence)

            # add 400 sequences at the time, more can cause problems with some database engines
            if len(new_sequences) > 400:
                db.engine.execute(Sequence.__table__.insert(), new_sequences)
                new_sequences = []

        # add the last set of sequences
        db.engine.execute(Sequence.__table__.insert(), new_sequences)

        return len(fasta_data.sequences.keys())

    @staticmethod
    def add_descriptions(filename, species_id):
        sequences = Sequence.query.filter_by(species_id=species_id).all()

        seq_dict = {}

        for s in sequences:
            seq_dict[s.name] = s

        with open(filename, "r") as f_in:
            for i, line in enumerate(f_in):
                name, description = line.strip().split('\t')

                if name in seq_dict.keys():
                    seq_dict[name].description = description

                if i % 400 == 0:
                    db.session.commit()

            db.session.commit()

    @staticmethod
    def export_cds(filename):
        sequences = Sequence.query.options(undefer('coding_sequence')).all()

        with open(filename, "w") as f_out:
            for s in sequences:
                print(">%s\n%s" % (s.name, s.coding_sequence), file=f_out)

    @staticmethod
    def export_protein(filename):
        sequences = Sequence.query.options(undefer('coding_sequence')).all()

        with open(filename, "w") as f_out:
            for s in sequences:
                print(">%s\n%s" % (s.name, s.protein_sequence), file=f_out)
