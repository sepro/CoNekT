from planet import db

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50, collation=SQL_COLLATION), unique=True)
    name = db.Column(db.String(200, collation=SQL_COLLATION))
    data_type = db.Column(db.Enum('genome', 'transcriptome', name='data_type'))
    ncbi_tax_id = db.Column(db.Integer)
    pubmed_id = db.Column(db.Integer)
    project_page = db.Column(db.Text)
    color = db.Column(db.String(7), default="#C7C7C7")
    highlight = db.Column(db.String(7), default="#DEDEDE")
    sequence_count = db.Column(db.Integer)
    network_count = db.Column(db.Integer)
    profile_count = db.Column(db.Integer)

    sequences = db.relationship('Sequence', backref='species', lazy='dynamic')
    networks = db.relationship('ExpressionNetworkMethod', backref='species', lazy='dynamic')
    profiles = db.relationship('ExpressionProfile', backref='species', lazy='dynamic')
    expression_specificities = db.relationship('ExpressionSpecificityMethod', backref='species', lazy='dynamic')

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
        self.sequence_count = 0
        self.profile_count = 0
        self.network_count = 0

    def __repr__(self):
        return str(self.id) + ". " + self.name

    @staticmethod
    def add(code, name, data_type='genome', ncbi_tax_id=None, pubmed_id=None, project_page=None,
            color="#C7C7C7", highlight="#DEDEDE"):

        new_species = Species(code, name, data_type=data_type, ncbi_tax_id=ncbi_tax_id, pubmed_id=pubmed_id,
                              project_page=project_page, color=color, highlight=highlight)

        species = Species.query.filter_by(code=code).first()

        # species is not in the DB yet, add it
        if species is None:
            try:
                db.session.add(new_species)
                db.session.commit()
            except:
                db.rollback()

            return new_species.id
        else:
            return species.id

    @staticmethod
    def update_counts():
        """
        To avoid long counts the number of sequences, profiles and networks can be precalculated and stored in the
        database using this function.
        """
        species = Species.query.all()

        for s in species:
            s.sequence_count = s.sequences.count()
            s.profile_count = s.profiles.count()
            s.network_count = s.networks.count()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
