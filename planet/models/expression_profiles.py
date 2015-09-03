from planet import db


class ExpressionProfile(db.Model):
    __tablename__ = 'expression_profiles'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    probe = db.Column(db.String(50))
    sequence_id = db.Column(db.String(50), db.ForeignKey('sequences.id'))
    profile = db.Column(db.Text)

    def __init__(self, probe, sequence_id, profile):
        self.probe = probe
        self.sequence_id = sequence_id
        self.profile = profile

