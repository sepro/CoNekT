from planet import db

class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200))
    data_type = db.Column(db.Enum('genome', 'transcriptome', name='data_type'))
    ncbi_tax_id = db.Column(db.Integer)
    pubmed_id = db.Column(db.Integer)
    project_page = db.Column(db.Text)

    sequences = db.relationship('Sequence', backref='species')

    def __repr__(self):
        return '<Species %d>' % self.id
