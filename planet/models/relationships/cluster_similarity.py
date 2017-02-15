from planet import db


class CoexpressionClusterSimilarity(db.Model):
    __tablename__ = 'coexpression_cluster_similarity'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'))

    gene_family_method_id = db.Column('gene_family_method_id', db.Integer, db.ForeignKey('gene_family_methods.id'),
                                      index=True)

    jaccard_index = db.Column(db.Float, index=True)
    p_value = db.Column(db.Float, index=True)
    corrected_p_value = db.Column(db.Float, index=True)

    source = db.relationship('CoexpressionCluster', lazy='joined', foreign_keys=[source_id],
                             cascade='all, delete-orphan', single_parent=True)
    target = db.relationship('CoexpressionCluster', lazy='joined', foreign_keys=[target_id],
                             cascade='all, delete-orphan', single_parent=True)

    gene_family_method = db.relationship('GeneFamilyMethod', lazy='joined')