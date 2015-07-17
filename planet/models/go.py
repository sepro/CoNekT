from planet import db

class GO(db.Model):
    __tablename__ = 'go'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.Text)
    type = db.Column(db.Enum('biological_process', 'molecular_function', 'cellular_component', name='go_type'))
    description = db.Column(db.Text)
    extended_go = db.Column(db.Text)

    def __init__(self, label, name, go_type, description, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.extended_go = extended_go

    def set_all(self, label, name, go_type, description, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.extended_go = extended_go
