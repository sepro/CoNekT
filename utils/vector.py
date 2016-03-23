from math import sqrt


def dot_prod(a, b):
    """
    Calculates the dot product of two lists with values

    :param a: first list
    :param b: second list
    :return: dot product (a . b)
    """
    return sum([i*j for (i, j) in zip(a, b)])


def norm(a):
    """
    Calculates the Frobenius norm for a list of values

    :param a: list of values
    :return: the Frobenius norm
    """
    return sqrt(sum([i**2 for i in a]))
