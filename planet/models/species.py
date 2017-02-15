from planet import db

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50, collation=SQL_COLLATION), unique=True)
    name = db.Column(db.String(200, collation=SQL_COLLATION))
    data_type = db.Column(db.Enum('genome', 'transcriptome', name='data_type'))
    color = db.Column(db.String(7), default="#C7C7C7")
    highlight = db.Column(db.String(7), default="#DEDEDE")
    sequence_count = db.Column(db.Integer)
    network_count = db.Column(db.Integer)
    profile_count = db.Column(db.Integer)
    description = db.Column(db.Text)

    sequences = db.relationship('Sequence', backref='species', lazy='dynamic', cascade='all, delete-orphan')
    networks = db.relationship('ExpressionNetworkMethod', backref='species', lazy='dynamic', cascade='all, delete-orphan')
    profiles = db.relationship('ExpressionProfile', backref='species', lazy='dynamic', cascade='all, delete-orphan')
    expression_specificities = db.relationship('ExpressionSpecificityMethod', backref='species', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, code, name, data_type='genome',
                 color="#C7C7C7", highlight="#DEDEDE", description=None):
        self.code = code
        self.name = name
        self.data_type = data_type
        self.color = color
        self.highlight = highlight
        self.sequence_count = 0
        self.profile_count = 0
        self.network_count = 0
        self.description = description

    def __repr__(self):
        return str(self.id) + ". " + self.name

    @staticmethod
    def add(code, name, data_type='genome',
            color="#C7C7C7", highlight="#DEDEDE", description=None):

        new_species = Species(code, name, data_type=data_type, color=color, highlight=highlight, description=description)

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
