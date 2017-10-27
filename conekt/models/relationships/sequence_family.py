from conekt import db


class SequenceFamilyAssociation(db.Model):
    __tablename__ = 'sequence_family'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))
    gene_family_id = db.Column(db.Integer, db.ForeignKey('gene_families.id', ondelete='CASCADE'))

    sequence = db.relationship('Sequence', backref=db.backref('family_associations',
                                                              lazy='dynamic',
                                                              passive_deletes=True), lazy='joined')
    family = db.relationship('GeneFamily', backref=db.backref('sequence_associations',
                                                              lazy='dynamic',
                                                              passive_deletes=True), lazy='joined')


