from planet import db

from planet.models.condition_tissue import ConditionTissue
from planet.models.expression.profiles import ExpressionProfile

import json


class CrossSpeciesExpressionProfile:

    @staticmethod
    def get_data(*sequence_ids):
        condition_tissue = ConditionTissue.query.filter(ConditionTissue.in_tree == 1).all()

        conditions = []

        for ct in condition_tissue:
            data = json.loads(ct.data)
            for label in data["order"]:
                if label not in conditions:
                    conditions.append(label)

        species_to_condition = {ct.species_id: ct for ct in condition_tissue}

        profiles = ExpressionProfile.query.filter(ExpressionProfile.sequence_id.in_(list(sequence_ids)))



