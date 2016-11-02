from planet import db

import json

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class ConditionTissue(db.Model):
    __tablename__ = 'conditions_tissue'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    name = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    data = db.Column(db.Text)

    @staticmethod
    def add(species_id, name, data):
        """
        Add conversion table to the database for a species

        :param species_id: internal id for the species
        :param name: name of the conversion table (will be shown on profile pages)
        :param data: dict with the conversion (key = condition, value = more general feature (e.g. tissue))
        """
        new_ct = ConditionTissue()

        new_ct.species_id = species_id
        new_ct.name = name
        new_ct.data = json.dumps(data)

        db.session.add(new_ct)
        db.session.commit()
