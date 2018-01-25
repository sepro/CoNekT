from conekt import db
from conekt.models.sequences import Sequence
from conekt.models.condition_tissue import ConditionTissue

import json
import contextlib
from collections import defaultdict
from statistics import mean
from math import log

from sqlalchemy.orm import joinedload, undefer
from flask import flash

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class ExpressionProfile(db.Model):
    __tablename__ = 'expression_profiles'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE'), index=True)
    probe = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'), index=True)
    profile = db.deferred(db.Column(db.Text))

    specificities = db.relationship('ExpressionSpecificity',
                                    backref=db.backref('profile', lazy='joined'),
                                    lazy='dynamic',
                                    cascade="all, delete-orphan",
                                    passive_deletes=True)

    def __init__(self, probe, sequence_id, profile):
        self.probe = probe
        self.sequence_id = sequence_id
        self.profile = profile

    @staticmethod
    def __profile_to_table(data):
        """
        Internal function to convert an expression profile (dict) to a tabular text

        :param data: Dict with expression profile
        :return: table (string)
        """
        output = [["condition", "mean", "min", "max"]]
        order = data["order"]

        for o in order:
            try:
                values = data["data"][o]
                output.append([o,
                               str(mean(values)),
                               str(min(values)),
                               str(max(values))
                               ])
            except Exception as e:
                print(e)

        return '\n'.join(['\t'.join(l) for l in output])

    @property
    def table(self):
        """
        Returns the condition expression as a tabular text file

        :return: table with data (string)
        """
        table = ExpressionProfile.__profile_to_table(json.loads(self.profile))

        return table

    def tissue_table(self, condition_tissue_id, use_means=True):
        """
        Returns the tissue expression as a tabular text file

        :param condition_tissue_id: condition_tissue_id for the conversion
        :param use_means: Use the mean of the condition (recommended)
        :return: table with data (string)
        """
        table = ExpressionProfile.__profile_to_table(self.tissue_profile(condition_tissue_id,
                                                                         use_means=use_means)
                                                     )
        return table

    @property
    def low_abundance(self, cutoff=10):
        """
        Checks if the mean expression value in any conditions in the plot is higher than the desired cutoff

        :param cutoff: cutoff for expression, default = 10
        :return: True in case of low abundance otherwise False
        """
        data = json.loads(self.profile)

        checks = [mean(v) > cutoff for _, v in data["data"].items()]

        return not any(checks)

    @staticmethod
    def convert_profile(condition_to_tissue, profile_data, use_means=True):
        """
        Convert a full, detailed profile into a more general summarized one using conversion table stored in the
        database

        :param condition_to_tissue: dict with conversion instructions
        :param profile_data: profile to convert
        :param use_means: use means of detailed condition if True otherwise use samples independently. Default True
        :return: New profile
        """
        tissues = list(set(condition_to_tissue['conversion'].values()))

        output = {}

        for t in tissues:
            valid_conditions = [k for k in profile_data['data'] if k in condition_to_tissue['conversion'] and condition_to_tissue['conversion'][k] == t]
            valid_values = []
            for k, v in profile_data['data'].items():
                if k in valid_conditions:
                    if use_means:
                        valid_values.append(mean(v))
                    else:
                        valid_values += v

            output[t] = valid_values if len(valid_values) > 0 else [0]

        return {'order': condition_to_tissue['order'],
                'colors': condition_to_tissue['colors'],
                'data': output}

    def tissue_profile(self, condition_tissue_id, use_means=True):
        """
        Applies a conversion to the profile, grouping several condition into one more general feature (e.g. tissue).

        :param condition_tissue_id: identifier of the conversion table
        :param use_means: store the mean of the condition rather than individual values. The matches the spm
        calculations better.
        :return: parsed profile
        """
        ct = ConditionTissue.query.get(condition_tissue_id)

        condition_to_tissue = json.loads(ct.data)
        profile_data = json.loads(self.profile)

        output = ExpressionProfile.convert_profile(condition_to_tissue, profile_data, use_means=use_means)

        return output

    @staticmethod
    def get_heatmap(species_id, probes, zlog=True, raw=False):
        """
        Returns a heatmap for a given species (species_id) and a list of probes. It returns a dict with 'order'
        the order of the experiments and 'heatmap' another dict with the actual data. Data is zlog transformed

        :param species_id: species id (internal database id)
        :param probes: a list of probes to include in the heatmap
        :param zlog: enable zlog transformation (otherwise normalization against highest expressed condition)
        """
        profiles = ExpressionProfile.query.options(undefer('profile')).filter_by(species_id=species_id).\
            filter(ExpressionProfile.probe.in_(probes)).all()

        order = []

        output = []

        not_found = [p.lower() for p in probes]

        for profile in profiles:
            name = profile.probe
            data = json.loads(profile.profile)
            order = data['order']
            experiments = data['data']

            with contextlib.suppress(ValueError):
                not_found.remove(profile.probe.lower())

            with contextlib.suppress(ValueError):
                not_found.remove(profile.sequence.name.lower())

            values = {}

            for o in order:
                values[o] = mean(experiments[o])

            row_mean = mean(values.values())
            row_max = max(values.values())

            for o in order:
                if zlog:
                    if row_mean == 0 or values[o] == 0:
                        values[o] = '-'
                    else:
                        values[o] = log(values[o]/row_mean, 2)
                else:
                    if row_max != 0 and not raw:
                        values[o] = values[o]/row_max

            output.append({"name": name,
                           "values": values,
                           "sequence_id": profile.sequence_id,
                           "shortest_alias":profile.sequence.shortest_alias})

        if len(not_found) > 0:
            flash("Couldn't find profile for: %s" % ",".join(not_found), "warning")

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

    @staticmethod
    def add_profile_from_lstrap(matrix_file, annotation_file, species_id, order_color_file=None):
        """
        Function to convert an (normalized) expression matrix (lstrap output) into a profile

        :param matrix_file: path to the expression matrix
        :param annotation_file: path to the file assigning samples to conditions
        :param species_id: internal id of the species
        :param order_color_file: tab delimited file that contains the order and color of conditions
        """
        annotation = {}

        with open(annotation_file, 'r') as fin:
            # get rid of the header
            _ = fin.readline()

            for line in fin:
                parts = line.strip().split('\t')
                if len(parts) > 1:
                    run, description = parts
                    annotation[run] = description

        order, colors = [], []
        if order_color_file is not None:
            with open(order_color_file, 'r') as fin:
                for line in fin:
                    try:
                        o, c = line.strip().split('\t')
                        order.append(o)
                        colors.append(c)
                    except Exception as _:
                        pass

        # build conversion table for sequences
        sequences = Sequence.query.filter_by(species_id=species_id).all()

        sequence_dict = {}  # key = sequence name uppercase, value internal id
        for s in sequences:
            sequence_dict[s.name.upper()] = s.id

        with open(matrix_file) as fin:
            # read header
            _, *colnames = fin.readline().rstrip().split()

            colnames = [c.replace('.htseq', '') for c in colnames]

            # determine order after annotation is not defined
            if order is None:
                order = []

                for c in colnames:
                    if c in annotation.keys():
                        if annotation[c] not in order:
                            order.append(annotation[c])

                order.sort()

            # read each line and build profile
            new_probes = []
            for line in fin:
                transcript, *values = line.rstrip().split()
                profile = defaultdict(list)

                for c, v in zip(colnames, values):
                    if c in annotation.keys():
                        condition = annotation[c]
                        profile[condition].append(float(v))

                new_probe = {"species_id": species_id,
                             "probe": transcript,
                             "sequence_id": sequence_dict[transcript.upper()] if transcript.upper() in sequence_dict.keys() else None,
                             "profile": json.dumps({"order": order,
                                                    "colors": colors,
                                                    "data": profile})
                             }

                new_probes.append(new_probe)

                if len(new_probes) > 400:
                    db.engine.execute(ExpressionProfile.__table__.insert(), new_probes)
                    new_probes = []

            db.engine.execute(ExpressionProfile.__table__.insert(), new_probes)
