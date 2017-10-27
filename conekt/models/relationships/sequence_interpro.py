from conekt import db


class SequenceInterproAssociation(db.Model):
    __tablename__ = 'sequence_interpro'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))
    interpro_id = db.Column(db.Integer, db.ForeignKey('interpro.id', ondelete='CASCADE'))
    start = db.Column(db.Integer, default=None)
    stop = db.Column(db.Integer, default=None)

    sequence = db.relationship('Sequence', backref=db.backref('interpro_associations',
                                                              lazy='dynamic',
                                                              passive_deletes=True), lazy='joined')

    domain = db.relationship('Interpro', backref=db.backref('sequence_associations',
                             lazy='dynamic', passive_deletes=True), lazy='joined')
