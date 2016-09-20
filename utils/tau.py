def tau(dist):
    """
    Calculates the Tau value for a list of expression values

    :param dist: list of values
    :return: tau value
    """
    n = len(dist)                   # number of values
    mxi = max(dist)                 # max value

    t = sum([1 - (x/mxi) for x in dist])/(n - 1)

    return t
