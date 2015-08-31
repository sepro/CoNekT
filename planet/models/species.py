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
    networks = db.relationship('ExpressionNetworkMethod', backref='species', lazy='dynamic')


    def __init__(self, code, name, data_type='genome', ncbi_tax_id=None, pubmed_id=None, project_page=None,
                 color="#C7C7C7", highlight="#DEDEDE"):
        self.code = code
        self.name = name
        self.data_type = data_type
        self.ncbi_tax_id = ncbi_tax_id
        self.pubmed_id = pubmed_id
        self.project_page = project_page
        self.color = color
        self.highlight = highlight

    def __repr__(self):
        return str(self.id) + ". " + self.name
