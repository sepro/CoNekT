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
        new_method = ExpressionSpecificityMethod()
        new_method.species_id = species_id
        new_method.description = description
        conditions = []

        profiles = db.engine.execute(db.select([ExpressionProfile.__table__.c.id, ExpressionProfile.__table__.c.profile]).
                                     where(ExpressionProfile.__table__.c.species_id == species_id)
                                     ).fetchall()

        for profile_id, profile in profiles:
            profile_data = json.loads(profile)
            for condition in profile_data['order']:
                if condition not in conditions:
                    conditions.append(condition)

        new_method.conditions = json.dumps(conditions)

        db.session.add(new_method)
        db.session.commit()

        specificities = []

        for profile_id, profile in profiles:
            profile_data = json.loads(profile)
            profile_means = {k: mean(v) for k, v in profile_data['data'].items()}

            for condition in profile_data['order']:
                score = expression_specificity(condition, profile_means)
                new_specificity = {
                    'profile_id': profile_id,
                    'condition': condition,
                    'score': score,
                    'method_id': new_method.id,
                }

                specificities.append(new_specificity)
                if len(specificities) > 400:
                    db.engine.execute(ExpressionSpecificity.__table__.insert(), specificities)
                    specificities = []

        db.engine.execute(ExpressionSpecificity.__table__.insert(), specificities)


class ExpressionSpecificity(db.Model):
    __tablename__ = 'expression_specificity'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('expression_profiles.id'), index=True)
    condition = db.Column(db.String(255), index=True)
    score = db.Column(db.Float, index=True)
    method_id = db.Column(db.Integer, db.ForeignKey('expression_specificity_method.id'), index=True)
