from conekt import db


class SequenceXRefAssociation(db.Model):
    __tablename__ = 'sequence_xref'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'), index=True)
    xref_id = db.Column(db.Integer, db.ForeignKey('xrefs.id', ondelete='CASCADE'), index=True)
