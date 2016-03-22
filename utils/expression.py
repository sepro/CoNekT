from utils.vector import dot_prod, norm


def expression_specificity(condition, profile):
    values = [v for k, v in profile.items()]
    vector = [v if k == condition else 0 for k, v in profile.items()]

    dot_product = dot_prod(values, vector)

    mul_len = norm(values) * norm(vector)

    if mul_len != 0:
        return dot_product/mul_len
    else:
        return 0
