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
    color = db.Column(db.String(7), default="#C7C7C7")
    highlight = db.Column(db.String(7), default="#DEDEDE")

    sequences = db.relationship('Sequence', backref='species', lazy='dynamic')

    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.color = "#C7C7C7"
        self.highlight = "#DEDEDE"

    def __repr__(self):
        return '<Species %d>' % self.id
