from planet import db

class GO(db.Model):
    __tablename__ = 'go'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Text)
    description = db.Column(db.Text)
    extended_go = db.Column(db.Text)
