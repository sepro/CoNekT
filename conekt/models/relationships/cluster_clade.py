from conekt import db


class ClusterCladeEnrichment(db.Model):
    __tablename__ = 'cluster_clade_enrichment'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id', ondelete='CASCADE'))
    clade_id = db.Column(db.Integer, db.ForeignKey('clades.id', ondelete='CASCADE'))

    gene_family_method_id = db.Column(db.Integer, db.ForeignKey('gene_family_methods.id', ondelete='CASCADE'))

    gene_family_method = db.relationship('GeneFamilyMethod', backref=db.backref('clade_enrichment',
                                                                                lazy='dynamic',
                                                                                passive_deletes=True),
                                         lazy='joined')

    cluster = db.relationship('CoexpressionCluster', backref=db.backref('clade_enrichment',
                                                                        lazy='dynamic',
                                                                        passive_deletes=True),
                              lazy='joined')

    clade = db.relationship('Clade', backref=db.backref('enriched_clusters',
                                                        lazy='dynamic',
                                                        passive_deletes=True),
                            lazy='joined')

    """
    Counts required to calculate the enrichment,
    store here for quick access
    """
    cluster_count = db.Column(db.Integer)
    cluster_size = db.Column(db.Integer)
    clade_count = db.Column(db.Integer)
    clade_size = db.Column(db.Integer)

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
        return self.clade_count*100/self.clade_size
