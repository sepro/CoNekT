from planet import db

import json
from statistics import mean
from math import log

from sqlalchemy.orm import joinedload, undefer

class ExpressionProfile(db.Model):
    __tablename__ = 'expression_profiles'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), index=True)
    probe = db.Column(db.String(50), index=True)
    sequence_id = db.Column(db.String(50), db.ForeignKey('sequences.id'), index=True)
    profile = db.deferred(db.Column(db.Text))

    def __init__(self, probe, sequence_id, profile):
        self.probe = probe
        self.sequence_id = sequence_id
        self.profile = profile

    @staticmethod
    def get_heatmap(species_id, probes):
        """
        Returns a heatmap for a given species (species_id) and a list of probes. It returns a dict with 'order'
        the order of the experiments and 'heatmap' another dict with the actual data. Data is zlog transformed

        :param species_id: species id (internal database id)
        :param probes: a list of probes to include in the heatmap
        """
        profiles = ExpressionProfile.query.options(undefer('profile')).filter_by(species_id=species_id).\
            filter(ExpressionProfile.probe.in_(probes)).all()

        order = []

        output = []

        for profile in profiles:
            name = profile.probe
            data = json.loads(profile.profile)
            order = data['order']
            experiments = data['data']

            values = {}

            for o in order:
                values[o] = mean(experiments[o])

            row_mean = mean(values.values())

            for o in order:
                if row_mean == 0 or values[o] == 0:
                    values[o] = 0
                else:
                    values[o] = log(values[o]/row_mean, 2)

            output.append({"name": name, "values": values})

        return {'order': order, 'heatmap_data': output}

    @staticmethod
    def get_profiles(species_id, probes):
        profiles = ExpressionProfile.query.\
            options(undefer('profile')).\
            filter(ExpressionProfile.probe.in_(probes)).\
            filter_by(species_id=species_id).\
            options(joinedload('sequence').load_only('name')).\
            all()

        return profiles
