def tau(values):
    """
    Calculates the Tau value for a list of expression values

    :param dist: list of values
    :return: tau value
    """
    n = len(values)                   # number of values
    mxi = max(values)                 # max value

    if mxi > 0:
        t = sum([1 - (x/mxi) for x in values])/(n - 1)

        return t
    else:
        return None
