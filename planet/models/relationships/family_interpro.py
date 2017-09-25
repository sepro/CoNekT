from planet import db


class FamilyInterproAssociation(db.Model):
    __tablename__ = 'family_interpro'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    gene_family_id = db.Column(db.Integer, db.ForeignKey('gene_families.id', ondelete='CASCADE'))
    interpro_id = db.Column(db.Integer, db.ForeignKey('interpro.id', ondelete='CASCADE'))
