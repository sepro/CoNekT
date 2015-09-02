from planet import db
from planet.models.relationships import sequence_interpro


class Interpro(db.Model):
    __tablename__ = 'interpro'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), unique=True, index=True)
    description = db.Column(db.Text)

    sequences = db.relationship('Sequence', secondary=sequence_interpro, lazy='dynamic')
    sequence_associations = db.relationship('SequenceInterproAssociation', backref='interpro', lazy='dynamic')

    def __init__(self, label, description):
        self.label = label
        self.description = description
