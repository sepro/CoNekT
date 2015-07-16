from planet import db
from sqlalchemy import Enum

from planet.models.relationships import sequence_go, sequence_interpro, sequence_family

class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    name = db.Column(db.Text)
    transcript = db.Column(db.Text)
    coding_sequence = db.Column(db.Text)
    type = db.Column(Enum('protein', 'TE', 'RNA', name='sequence_type'))
    is_mitochondrial = db.Column(db.Boolean)
    is_chloroplast = db.Column(db.Boolean)

    go_labels = db.relationship('go', secondary=sequence_go,
                                backref=db.backref('sequences', lazy='dynamic'),
                                lazy='dynamic')

    interpro_domains = db.relationship('interpro', secondary=sequence_interpro,
                                       backref=db.backref('sequences', lazy='dynamic'),
                                       lazy='dynamic')
    families = db.relationship('go', secondary=sequence_family,
                               backref=db.backref('sequences', lazy='dynamic'),
                               lazy='dynamic')
