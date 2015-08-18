from planet import db


sequence_go = db.Table('sequence_go',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id')),
                       db.Column('go_id', db.Integer, db.ForeignKey('go.id'))
                       )

sequence_interpro = db.Table('sequence_interpro',
                             db.Column('id', db.Integer, primary_key=True),
                             db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id')),
                             db.Column('interpro_id', db.Integer, db.ForeignKey('interpro.id')),
                             )

sequence_family = db.Table('sequence_family',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id')),
                           db.Column('gene_family_id', db.Integer, db.ForeignKey('gene_families.id'))
                           )

sequence_coexpression_cluster = db.Table('sequence_coexpression_cluster',
                                         db.Column('id', db.Integer, primary_key=True),
                                         db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id')),
                                         db.Column('coexpression_cluster_id', db.Integer,
                                                   db.ForeignKey('coexpression_clusters.id'))
                                         )


class SequenceFamilyAssociation(db.Model):
    __tablename__ = 'sequence_family'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    gene_family_id = db.Column(db.Integer, db.ForeignKey('gene_families.id'))

    sequence = db.relationship('Sequence', lazy='select')
    family = db.relationship('GeneFamily', lazy='select')
