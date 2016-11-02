from planet import db
from planet.models.relationships import sequence_go, SequenceGOAssociation
from planet.models.sequences import Sequence

import json

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class GO(db.Model):
    __tablename__ = 'go'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    name = db.Column(db.Text)
    type = db.Column(db.Enum('biological_process', 'molecular_function', 'cellular_component', name='go_type'))
    description = db.Column(db.Text)
    obsolete = db.Column(db.Boolean)
    is_a = db.Column(db.Text)
    extended_go = db.Column(db.Text)
    species_counts = db.Column(db.Text)

    sequences = db.relationship('Sequence', secondary=sequence_go, lazy='dynamic')
    sequence_associations = db.relationship('SequenceGOAssociation', backref=db.backref('go', lazy='joined'), lazy='dynamic')

    enriched_clusters = db.relationship('ClusterGOEnrichment',
                                        backref=db.backref('go', lazy='joined'),
                                        lazy='dynamic')

    def __init__(self, label, name, go_type, description, obsolete, is_a, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.obsolete = obsolete
        self.is_a = is_a
        self.extended_go = extended_go
        self.species_counts = ""

    def set_all(self, label, name, go_type, description, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.extended_go = extended_go
        self.species_counts = ""

    def species_occurrence(self, species_id):
        """
        count how many genes have the current GO term in a given species

        :param species_id: internal id of the selected species
        :return: count of sequences with this term associated
        """
        count = 0
        sequences = self.sequences.all()

        for s in sequences:
            if s.species_id == species_id:
                count += 1

        return count

    @staticmethod
    def update_species_counts():
        """
        adds phylo-profile to each go-label, results are stored in the database
        """
        # link species to sequences
        sequences = db.engine.execute(db.select([Sequence.__table__.c.id, Sequence.__table__.c.species_id])).fetchall()

        sequence_to_species = {}
        for seq_id, species_id in sequences:
            sequence_to_species[seq_id] = int(species_id)

        # get go for all genes
        associations = db.engine.execute(
            db.select([SequenceGOAssociation.__table__.c.sequence_id,
                       SequenceGOAssociation.__table__.c.go_id], distinct=True))\
            .fetchall()

        count = {}
        for seq_id, go_id in associations:
            species_id = sequence_to_species[seq_id]

            if go_id not in count.keys():
                count[go_id] = {}

            if species_id not in count[go_id]:
                count[go_id][species_id] = 1
            else:
                count[go_id][species_id] += 1

        # update counts
        for go_id, data in count.items():
            db.engine.execute(db.update(GO.__table__)
                              .where(GO.__table__.c.id == go_id)
                              .values(species_counts=json.dumps(data)))
