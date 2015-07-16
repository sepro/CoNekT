from planet import db

class GO(db.Model):
    __tablename__ = 'go'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.Text)
    type = db.Column(db.Enum('biological_process', 'molecular_function', 'cellular_component', name='go_type'))
    description = db.Column(db.Text)
    extended_go = db.Column(db.Text)
