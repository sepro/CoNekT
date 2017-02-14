from planet import db


class SequenceCoexpressionClusterAssociation(db.Model):
    __tablename__ = 'sequence_coexpression_cluster'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    probe = db.Column(db.String(50), index=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    coexpression_cluster_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))

    sequence = db.relationship('Sequence', backref=db.backref('coexpression_cluster_associations',
                                                              lazy='dynamic',
                                                              cascade="all, delete-orphan"),
                               lazy='joined')
    coexpression_cluster = db.relationship('CoexpressionCluster',
                                           backref=db.backref('sequence_associations',
                                                              lazy='dynamic',
                                                              cascade="all, delete-orphan"),
                                           lazy='joined')