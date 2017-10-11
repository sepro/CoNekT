from planet.models.condition_tissue import ConditionTissue
from planet.models.expression.profiles import ExpressionProfile

import json
from statistics import mean

from sqlalchemy.orm import undefer


class CrossSpeciesExpressionProfile:

    def __init__(self):
        self.condition_tissue = ConditionTissue.query.filter(ConditionTissue.in_tree == 1).all()

        self.conditions, self.colors = [], []

        for ct in self.condition_tissue:
            data = json.loads(ct.data)
            for label, color in zip(data["order"], data["colors"]):
                if label not in self.conditions:
                    self.conditions.append(label)
                    self.colors.append(color)

                self.species_to_condition = {ct.species_id: ct for ct in self.condition_tissue}

    def get_data(self, *sequence_ids):
        profiles = ExpressionProfile.query.filter(ExpressionProfile.sequence_id.in_(list(sequence_ids))).\
            options(undefer('profile')).all()

        converted_profiles = []

        for p in profiles:
            if p.species_id in self.species_to_condition.keys():
                current_profile = p.tissue_profile(self.species_to_condition[p.species_id].id)

                parsed_profile = {
                    "order": self.conditions,
                    "colors": self.colors,
                    "data": {c: mean(current_profile["data"][c]) if c in current_profile["data"].keys() else None
                             for c in self.conditions}
                    }

                converted_profiles.append(
                    {
                        "sequence_id": p.sequence_id,
                        "species_id": p.species_id,
                        "profile": parsed_profile
                    }
                )

        return converted_profiles
