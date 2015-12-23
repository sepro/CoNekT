from planet import db
from planet.models.relationships import sequence_interpro
from config import SQL_COLLATION

from sqlalchemy.orm import joinedload

class Interpro(db.Model):
    __tablename__ = 'interpro'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    description = db.Column(db.Text)

    clade_id = db.Column(db.Integer, db.ForeignKey('clades.id'), index=True)

    sequences = db.relationship('Sequence', secondary=sequence_interpro, lazy='dynamic')
    sequence_associations = db.relationship('SequenceInterproAssociation',
                                            backref=db.backref('interpro', lazy='joined'),
                                            lazy='dynamic')

    def __init__(self, label, description):
        self.label = label
        self.description = description

    @property
    def species_codes(self):
        """
        Finds all species the family has genes from
        :return: a list of all species (codes)
        """

        sequences = self.sequences.options(joinedload('species')).all()

        output = []

        for s in sequences:
            if s.species.code not in output:
                output.append(s.species.code)

        return output

    @property
    def species_counts(self):
        """
        Generates a phylogenetic profile of a gene family
        :return: a dict with counts per species (codes are keys)
        """

        sequences = self.sequences.options(joinedload('species')).all()

        output = {}

        for s in sequences:
            if s.species.code not in output:
                output[s.species.code] = 1
            else:
                output[s.species.code] += 1

        return output