from planet import db
from planet.models.relationships import sequence_family

class GeneFamilyMethod(db.Model):
    __tablename__ = 'gene_family_methods'
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.Text)
    family_count = db.Column(db.Integer)

    families = db.relationship('GeneFamily', backref='method', lazy='dynamic')

    def __init__(self, method):
        self.method = method

    @staticmethod
    def update_count():
        methods = GeneFamilyMethod.query.all()

        for m in methods:
            m.family_count = m.families.count()

        try:
            db.session.commit()
        except:
            db.session.rollback()

class GeneFamily(db.Model):
    __tablename__ = 'gene_families'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('gene_family_methods.id'))
    name = db.Column(db.String(50), unique=True, index=True)

    sequences = db.relationship('Sequence', secondary=sequence_family, lazy='dynamic')

    def __init__(self, name):
        self.name = name
