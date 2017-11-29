from conekt.models.condition_tissue import ConditionTissue
from conekt.models.expression.profiles import ExpressionProfile

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
                    "data": {},
                    "raw_data": {c: max(current_profile["data"][c]) if c in current_profile["data"].keys() else None
                             for c in self.conditions}
                    }

                # detect low expressed genes before normalization
                low_expressed = all(
                    [value < 10 for value in parsed_profile["raw_data"].values() if value is not None])

                # normalize profile
                min_value = min([i if i is not None else 0 for i in parsed_profile["raw_data"].values()])
                max_value = max([i if i is not None else 0 for i in parsed_profile["raw_data"].values()])

                if max_value > 0:
                    for c in self.conditions:
                        if parsed_profile["raw_data"][c] is not None:
                            parsed_profile["data"][c] = parsed_profile["raw_data"][c]/max_value
                        else:
                            parsed_profile["data"][c] = None

                converted_profiles.append(
                    {
                        "sequence_id": p.sequence_id,
                        "sequence_name": p.sequence.name if p.sequence is not None else None,
                        "shortest_alias": p.sequence.shortest_alias if p.sequence is not None else None,
                        "species_id": p.species_id,
                        "low_expressed": 1 if low_expressed else 0,
                        "profile": parsed_profile,
                        "min_expression": min_value,
                        "max_expression": max_value
                    }
                )

        return converted_profiles

    def get_heatmap(self, *sequence_ids, option='raw'):
        data = self.get_data(*sequence_ids)

        output = {
            'order': [],
            'heatmap_data': []
        }

        for d in data:
            if "profile" in d.keys() and "order" in d["profile"].keys():
                output['order'] = d["profile"]["order"]
                break

        key = 'raw_data' if option == 'raw' else 'data'

        for d in data:
            output['heatmap_data'].append({
                'sequence_id': d['sequence_id'],
                'name': d['sequence_name'],
                'shortest_alias': d['shortest_alias'],
                'values': {k: v if v is not None else '-' for k, v in d['profile'][key].items()}
            })

        return output
