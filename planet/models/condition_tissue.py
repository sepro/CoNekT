from planet import db
from config import SQL_COLLATION

import json


class ConditionTissue(db.Model):
    __tablename__ = 'conditions_tissue'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    name = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    data = db.Column(db.Text)

    @staticmethod
    def add(species_id, name, data):
        new_ct = ConditionTissue()

        new_ct.species_id = species_id
        new_ct.name = name
        new_ct.data = json.dumps(data)

        db.session.add(new_ct)
        db.session.commit()
