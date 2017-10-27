from conekt import db


class ClusterGOEnrichment(db.Model):
    __tablename__ = 'cluster_go_enrichment'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id', ondelete='CASCADE'))
    go_id = db.Column(db.Integer, db.ForeignKey('go.id', ondelete='CASCADE'))

    cluster = db.relationship('CoexpressionCluster', backref=db.backref('go_enrichment',
                                                                        lazy='dynamic',
                                                                        passive_deletes=True),
                              lazy='joined')

    go = db.relationship('GO', backref=db.backref('enriched_clusters',
                                                  lazy='dynamic',
                                                  passive_deletes=True),
                         lazy='joined')

    """
    Counts required to calculate the enrichment,
    store here for quick access
    """
    cluster_count = db.Column(db.Integer)
    cluster_size = db.Column(db.Integer)
    go_count = db.Column(db.Integer)
    go_size = db.Column(db.Integer)

    """
    Enrichment score (log-transformed), p-value and corrected p-value. Calculated using the hypergeometric
    distribution and applying FDR correction (aka. BH)
    """
    enrichment = db.Column(db.Float)
    p_value = db.Column(db.Float)
    corrected_p_value = db.Column(db.Float)

    @property
    def cluster_percentage(self):
        return self.cluster_count*100/self.cluster_size

    @property
    def genome_percentage(self):
        return self.go_count*100/self.go_size