from planet import create_app
from planet.models.expression_profiles import ExpressionProfile

from sqlalchemy.orm import undefer
from sqlalchemy.sql.expression import func

from utils.expression import max_spm

import json
from statistics import mean, stdev
from random import normalvariate

app = create_app('config')

with app.app_context():
    profiles = ExpressionProfile.query.filter(ExpressionProfile.species_id == 1).order_by(func.random()).options(undefer('profile')).limit(10000)

    with open('./data/random_max_spm.txt', "w") as f:
        for p in profiles:
            if p.profile is not None:
                profile_data = json.loads(p.profile)

                values = [float(sum(v)) for k, v in profile_data['data'].items()]
                mean_value = mean(values)
                sd = stdev(values)

                for _ in range(10):
                    random_values = []

                    while len(random_values) < len(values):
                        r = normalvariate(mean_value, sd)
                        if r >= 0:
                            random_values.append(r)

                    rand_mean = mean(random_values)
                    rand_sd = stdev(random_values)

                    rand_max_spm = max_spm({c: v for c, v in enumerate(random_values)})['score']

                    print(rand_max_spm, file=f)
