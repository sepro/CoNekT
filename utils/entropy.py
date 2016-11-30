from math import log2
from bisect import bisect


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


def entropy_from_values(values, num_bins=20):
    """
    builds the distribution and calculates the entropy for a list of values


    :param values: list of values
    :param num_bins: number of bins to generate for the distribution, default 20
    :return: entropy
    """

    hist = []

    bins = [b/num_bins for b in range(0, num_bins)]

    v_max = max(values)

    if v_max > 0:
        n_values = [v/v_max for v in values]
        hist = [0] * num_bins

        for v in n_values:
            b = bisect(bins, v)
            hist[b-1] += 1

    return entropy(hist)
