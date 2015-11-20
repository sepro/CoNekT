from planet import db
from planet.models.relationships import sequence_go
from planet.models.sequences import Sequence
from config import SQL_COLLATION

from sqlalchemy import func
from sqlalchemy.orm import joinedload

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

    def set_all(self, label, name, go_type, description, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.extended_go = extended_go

    def species_occurrence(self, species_id):
        sequences = self.sequences.filter_by(species_id=species_id).count()

        return sequences