from planet import db


class SequenceFamilyAssociation(db.Model):
    __tablename__ = 'sequence_family'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    gene_family_id = db.Column(db.Integer, db.ForeignKey('gene_families.id'))

    sequence = db.relationship('Sequence', backref=db.backref('family_associations',
                                                              lazy='dynamic',
                                                              cascade='all, delete-orphan'), lazy='joined')
    family = db.relationship('GeneFamily', backref=db.backref('sequence_associations',
                                                              lazy='dynamic',
                                                              cascade='all, delete-orphan'), lazy='joined')


