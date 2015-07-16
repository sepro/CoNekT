from planet import db

sequence_go = db.Table('sequence_go',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('sequence_id', db.Integer, db.ForeignKey('sequences.id')),
                       db.Column('go_id', db.Integer, db.ForeignKey('go.id'))
                       )
