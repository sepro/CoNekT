from planet import db
from planet.models.relationships import sequence_go

class GO(db.Model):
    __tablename__ = 'go'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.Text)
    type = db.Column(db.Enum('biological_process', 'molecular_function', 'cellular_component', name='go_type'))
    description = db.Column(db.Text)
    obsolete = db.Column(db.Boolean)
    is_a = db.Column(db.Text)
    extended_go = db.Column(db.Text)

    sequences = db.relationship('Sequence', secondary=sequence_go, lazy='dynamic')

    def __init__(self, label, name, go_type, description, obsolete, is_a, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.obsolete = obsolete
        self.is_a = is_a
        self.extended_go = extended_go

    def set_all(self, label, name, go_type, description, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.extended_go = extended_go
