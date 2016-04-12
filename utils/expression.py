from utils.vector import dot_prod, norm


def expression_specificity(condition, profile):
    values = [v for k, v in profile.items()]
    vector = [v if k == condition else 0 for k, v in profile.items()]

    dot_product = dot_prod(values, vector)

    mul_len = norm(values) * norm(vector)

    return dot_product/mul_len if mul_len != 0 else 0


def max_spm(profile, substract_background=False):
    conditions = [k for k, v in profile.items()]

    if substract_background:
        minimum = min(list(profile.values()))
        for k in profile.keys():
            profile[k] -= minimum

    spm_values = [{'condition': c, 'score': expression_specificity(c, profile)} for c in conditions]

    # sort spm_values high to low
    spm_values = sorted(spm_values, key=lambda x: x['score'], reverse=True)

    if len(spm_values) > 0:
        return spm_values[0]
    else:
        return None