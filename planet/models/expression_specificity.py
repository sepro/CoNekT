from planet import db
from planet.models.expression_profiles import ExpressionProfile
from utils.expression import expression_specificity

import json
from statistics import mean


class ExpressionSpecificityMethod(db.Model):
    __tablename__ = 'expression_specificity_method'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    conditions = db.Column(db.Text)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), index=True)

    specificities = db.relationship('ExpressionSpecificity', backref='method', lazy='dynamic')

    @staticmethod
    def calculate_specificities(species_id, description):
        """
        Function that calculates condition specificities for each profile. No grouping is applied, each condition is
        used as is

        :param species_id: internal species ID
        :param description: description for the method to determine the specificity
        """

        conditions = []

        # get profile from the database (ORM free for speed)
        profiles = db.engine.execute(db.select([ExpressionProfile.__table__.c.id, ExpressionProfile.__table__.c.profile]).
                                     where(ExpressionProfile.__table__.c.species_id == species_id)
                                     ).fetchall()

        # detect all conditions
        for profile_id, profile in profiles:
            profile_data = json.loads(profile)
            for condition in profile_data['order']:
                if condition not in conditions:
                    conditions.append(condition)

        # convert list into dictionary and run function
        conditions_dict = {k: k for k in conditions}
        ExpressionSpecificityMethod.calculate_tissue_specificities(species_id, description, conditions_dict)

    @staticmethod
    def calculate_tissue_specificities(species_id, description, condition_to_tissue):
        """
        Function calculates tissue specific genes based on the expression conditions. A dict is required to link
        specific conditions to the correct tissues. This also allows conditions to be excluded in case they are
        unrelated with a specific tissue.


        :param species_id: internal species ID
        :param description: description for the method to determine the specificity
        :param condition_to_tissue: dict to connect a condition to a tissue
        """
        new_method = ExpressionSpecificityMethod()
        new_method.species_id = species_id
        new_method.description = description
        tissues = list(set(condition_to_tissue.values()))

        # get profile from the database (ORM free for speed)
        profiles = db.engine.execute(db.select([ExpressionProfile.__table__.c.id, ExpressionProfile.__table__.c.profile]).
                                     where(ExpressionProfile.__table__.c.species_id == species_id)
                                     ).fetchall()

        new_method.conditions = json.dumps(tissues)

        db.session.add(new_method)
        db.session.commit()

        # detect specifities and add to the database
        specificities = []

        for profile_id, profile in profiles:
            # prepare profile data for calculation
            profile_data = json.loads(profile)
            profile_means = {}
            for t in tissues:
                count = 0
                total_sum = 0
                valid_conditions = [k for k in profile_data['data'] if k in condition_to_tissue and condition_to_tissue[k] == t]
                for k, v in profile_data['data'].items():
                    if k in valid_conditions:
                        count += len(v)
                        total_sum += sum(v)

                profile_means[t] = total_sum/count if count != 0 else 0

            # determine spm score for each condition
            profile_specificities = []

            for t in tissues:
                score = expression_specificity(t, profile_means)
                new_specificity = {
                    'profile_id': profile_id,
                    'condition': t,
                    'score': score,
                    'method_id': new_method.id,
                }

                profile_specificities.append(new_specificity)

            # sort conditions and add top 2 to array
            profile_specificities = sorted(profile_specificities, key=lambda x: x['score'], reverse=True)

            specificities += profile_specificities[:2]

            # write specificities to db if there are more than 400 (ORM free for speed)
            if len(specificities) > 400:
                db.engine.execute(ExpressionSpecificity.__table__.insert(), specificities)
                specificities = []

        # write remaining specificities to the db
        db.engine.execute(ExpressionSpecificity.__table__.insert(), specificities)


class ExpressionSpecificity(db.Model):
    __tablename__ = 'expression_specificity'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('expression_profiles.id'), index=True)
    condition = db.Column(db.String(255), index=True)
    score = db.Column(db.Float, index=True)
    method_id = db.Column(db.Integer, db.ForeignKey('expression_specificity_method.id'), index=True)
