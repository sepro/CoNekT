
def expression_specificity(condition, profile):
    values = [v for k, v in profile.items()]
    vector = [v if k == condition else 0 for k, v in profile.items()]

    print(values, vector)