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

        profiles = db.engine.execute(db.select([ExpressionProfile.__table__.c.id, ExpressionProfile.__table__.c.profile]).
                                     where(ExpressionProfile.__table__.c.species_id == species_id)
                                     ).fetchall()

        for profile_id, profile in profiles:
            profile_data = json.loads(profile)
            profile_mean = {k: mean(v) for k, v in profile_data['data'].items()}

            print(profile_id, profile_mean)
            for condition in profile_data['order']:
                score = expression_specificity(condition, profile_mean)


class ExpressionSpecificity(db.Model):
    __tablename__ = 'expression_specificity'

    id = db.Column(db.Integer, primary_key=True)
    profile = db.Column(db.Integer, db.ForeignKey('expression_profiles.id'), index=True)
    condition = db.Column(db.String(255), index=True)
    score = db.Column(db.Float, index=True)
    method_id = db.Column(db.Integer, db.ForeignKey('expression_specificity_method.id'), index=True)
