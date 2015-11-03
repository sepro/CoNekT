from planet import db
from planet.models.gene_families import GeneFamily

import json


class Clade(db.Model):
    __tablename__ = 'clades'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50, collation='NOCASE'), unique=True, index=True)
    species = db.Column(db.Text(collation='NOCASE'))
    species_count = db.Column(db.Integer)

    families = db.relationship('GeneFamily', backref='clade', lazy='dynamic')

    def __init__(self, name, species):
        self.name = name
        self.species = json.dumps(species)

    def __repr__(self):
        return str(self.id) + ". " + self.name

    @staticmethod
    def update_clades():
        """
        Loop over all families and determine what clade they belong too
        """
        clades = Clade.query.all()
        families = GeneFamily.query.all()

        for f in families:
            pass

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
