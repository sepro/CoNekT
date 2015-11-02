from planet import db


class XRef(db.Model):
    __tablename__ = 'xrefs'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50, collation='NOCASE'), index=True)
    name = db.Column(db.String(50, collation='NOCASE'), index=True)
    url = db.Column(db.Text())

