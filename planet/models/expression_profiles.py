from planet import db
from planet.models.condition_tissue import ConditionTissue

from utils.entropy import entropy

import json
from bisect import bisect
from statistics import mean
from math import log

from sqlalchemy.orm import joinedload, undefer, noload

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class ExpressionProfile(db.Model):
    __tablename__ = 'expression_profiles'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), index=True)
    probe = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'), index=True)
    profile = db.deferred(db.Column(db.Text))

    specificities = db.relationship('ExpressionSpecificity', backref=db.backref('profile', lazy='joined'), lazy='dynamic')

    def __init__(self, probe, sequence_id, profile):
        self.probe = probe
        self.sequence_id = sequence_id
        self.profile = profile

    def tissue_profile(self, condition_tissue_id):
        ct = ConditionTissue.query.get(condition_tissue_id)

        condition_to_tissue = json.loads(ct.data)
        profile_data = json.loads(self.profile)

        tissues = list(set(condition_to_tissue.values()))

        output = {}

        for t in tissues:
            valid_conditions = [k for k in profile_data['data'] if k in condition_to_tissue and condition_to_tissue[k] == t]
            valid_values = []
            for k, v in profile_data['data'].items():
                if k in valid_conditions:
                    valid_values += v

            output[t] = valid_values if len(valid_values) > 0 else [0]

        return {'order': tissues, 'data': output}

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
    def get_profiles(species_id, probes, limit=1000):
        """
        Gets the data for a set of probes (including the full profiles), a limit can be provided to avoid overly
        long queries

        :param species_id: internal id of the species
        :param probes: probe names to fetch
        :param limit: maximum number of probes to get
        :return: List of ExpressionProfile objects including the full profiles
        """
        profiles = ExpressionProfile.query.\
            options(undefer('profile')).\
            filter(ExpressionProfile.probe.in_(probes)).\
            filter_by(species_id=species_id).\
            options(joinedload('sequence').load_only('name').noload('xrefs')).\
            limit(limit).all()

        return profiles
