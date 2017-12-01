from conekt import db


class CoexpressionClusterSimilarity(db.Model):
    __tablename__ = 'coexpression_cluster_similarity'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id', ondelete='CASCADE'))
    target_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id', ondelete='CASCADE'))

    gene_family_method_id = db.Column('gene_family_method_id', db.Integer, db.ForeignKey('gene_family_methods.id', ondelete='CASCADE'),
                                      index=True)

    jaccard_index = db.Column(db.Float, index=True)
    p_value = db.Column(db.Float, index=True)
    corrected_p_value = db.Column(db.Float, index=True)

    source = db.relationship('CoexpressionCluster', backref=db.backref('similarity_sources',
                                                                       lazy='dynamic',
                                                                       passive_deletes=True),
                             lazy='joined', foreign_keys=[source_id])

    target = db.relationship('CoexpressionCluster', backref=db.backref('similarity_targets',
                                                                       lazy='dynamic',
                                                                       passive_deletes=True)
                             , lazy='joined', foreign_keys=[target_id])

    gene_family_method = db.relationship('GeneFamilyMethod',
                                         backref=db.backref('CoexpressionClusterSimilarities', passive_deletes=True),
                                         lazy='joined')

    @staticmethod
    def empty_table():
        """
        Delete all content from this table. Use carefully !
        """
        CoexpressionClusterSimilarity.query.delete()
