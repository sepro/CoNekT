from math import log2


def entropy(dist):
    """
    Calculates the entropy for a given distribution (!)

    :param dist: list with the counts for each bin
    :return: entropy
    """
    e = 0
    l = sum(dist)

    for d in dist:
        d_x = d/l
        if d_x > 0:
            e += - d_x*log2(d_x)

    return e
