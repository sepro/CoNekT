from conekt import db


class FamilyXRefAssociation(db.Model):
    __tablename__ = 'family_xref'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    gene_family_id = db.Column(db.Integer, db.ForeignKey('gene_families.id', ondelete='CASCADE'))
    xref_id = db.Column(db.Integer, db.ForeignKey('xrefs.id', ondelete='CASCADE'))
