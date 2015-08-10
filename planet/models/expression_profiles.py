from planet import db

class ExpressionProfile(db.Model):
    __tablename__ = 'expression_profiles'
    id = db.Column(db.Integer, primary_key=True)
    gene_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    data = db.Column(db.Text())
