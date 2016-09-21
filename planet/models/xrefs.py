from planet import db

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class XRef(db.Model):
    __tablename__ = 'xrefs'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    url = db.Column(db.Text())

