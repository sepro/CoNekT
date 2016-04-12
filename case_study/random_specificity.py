from planet import create_app
from planet.models.expression_profiles import ExpressionProfile

from sqlalchemy.orm import undefer
from sqlalchemy.sql.expression import func

from utils.expression import max_spm

import json
from statistics import mean, stdev
from random import lognormalvariate
from sys import argv


def write_random_spms(species_id, filename):
    app = create_app('config')

    with app.app_context():
        profiles = ExpressionProfile.query.filter(ExpressionProfile.species_id == species_id).order_by(func.random()).options(undefer('profile')).limit(10000)

        with open(filename, "w") as f:
            for p in profiles:
                if p.profile is not None:
                    profile_data = json.loads(p.profile)

                    values = [float(sum(v)) for k, v in profile_data['data'].items()]
                    mean_value = mean(values)
                    sd = stdev(values)

                    for _ in range(10):
                        random_values = []

                        while len(random_values) < len(values):
                            r = lognormalvariate(mean_value, sd)
                            if r >= 0:
                                random_values.append(r)

                        rand_mean = mean(random_values)
                        rand_sd = stdev(random_values)

                        rand_max_spm = max_spm({c: v for c, v in enumerate(random_values)})['score']

                        print(rand_max_spm, file=f)

if __name__ == "__main__":
    write_random_spms(int(argv[1]), argv[2])