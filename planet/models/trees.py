from planet import db

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class TreeMethod(db.Model):
    __tablename__ = 'tree_methods'
    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.Text)

    coexpression_clustering_method_id = db.Column(db.Integer,
                                                  db.ForeignKey('coexpression_clustering_methods.id'),
                                                  index=True)

    trees = db.relationship('Tree',
                            backref=db.backref('method', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')


class Tree(db.Model):
    __tablename__ = 'trees'
    id = db.Column(db.Integer, primary_key=True)

    label = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    data = db.Column(db.Text)

    method_id = db.Column(db.Integer, db.ForeignKey('tree_methods.id'), index=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('coexpression_clusters.id'), index=True)
