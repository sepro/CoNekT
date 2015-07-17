from planet import db

from planet.models.relationships import sequence_go, sequence_interpro, sequence_family, sequence_coexpression_cluster

class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    name = db.Column(db.String(50), index=True)
    transcript = db.Column(db.Text)
    coding_sequence = db.Column(db.Text)
    type = db.Column(db.Enum('protein_coding', 'TE', 'RNA', name='sequence_type'))
    is_mitochondrial = db.Column(db.Boolean)
    is_chloroplast = db.Column(db.Boolean)

    go_labels = db.relationship('go', secondary=sequence_go,
                                backref=db.backref('sequences', lazy='dynamic'),
                                lazy='dynamic')

    interpro_domains = db.relationship('interpro', secondary=sequence_interpro,
                                       backref=db.backref('sequences', lazy='dynamic'),
                                       lazy='dynamic')
    families = db.relationship('gene_families', secondary=sequence_family,
                               backref=db.backref('sequences', lazy='dynamic'),
                               lazy='dynamic')

    coexpression_clusters = db.relationship('coexpression_clusters', secondary=sequence_coexpression_cluster,
                                            backref=db.backref('sequences', lazy='dynamic'),
                                            lazy='dynamic')
