from planet.models.condition_tissue import ConditionTissue
from planet.models.expression.profiles import ExpressionProfile

import json
from statistics import mean
from heapq import merge
from collections import OrderedDict

from sqlalchemy.orm import undefer


class CrossSpeciesExpressionProfile:

    def __init__(self):
        self.condition_tissue = ConditionTissue.query.filter(ConditionTissue.in_tree == 1).all()

        # Way to merge various (potentially incomplete) lists and preserve the order (as good as possible)
        merged_conditions = list(merge(*[json.loads(ct.data)["order"] for ct in self.condition_tissue]))

        # Make list unique keeping the element with the highest index (reason for double reverse)
        self.conditions = list(reversed(        # reverse again and convert to list
            list(OrderedDict.fromkeys(          # make list unique
                reversed(merged_conditions))    # reverse input
            )
        ))

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
                    "data": {c: mean(current_profile["data"][c]) if c in current_profile["data"].keys() else None
                             for c in self.conditions}
                    }

                low_expressed = all([value < 10 if value is not None else False for value in parsed_profile["data"].values()])

                converted_profiles.append(
                    {
                        "sequence_id": p.sequence_id,
                        "species_id": p.species_id,
                        "low_expressed": 1 if low_expressed else 0,
                        "profile": parsed_profile
                    }
                )

        return converted_profiles
