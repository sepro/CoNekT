from math import log, exp
from mpmath import loggamma


def logchoose(ni, ki):
    try:
        lgn1 = loggamma(ni+1)
        lgk1 = loggamma(ki+1)
        lgnk1 = loggamma(ni-ki+1)
    except ValueError:
        #print ni,ki
        raise ValueError
    return lgn1 - (lgnk1 + lgk1)


def gauss_hypergeom(X, n, m, N):
    assert N >= m, 'Number of items %i must be larger than the number of marked items %i' % (N, m)
    assert m >= X, 'Number of marked items %i must be larger than the number of sucesses %i' % (m, X)
    assert n >= X, 'Number of draws %i must be larger than the number of sucesses %i' % (n, X)
    assert N >= n, 'Number of draws %i must be smaller than the total number of items %i' % (n, N)

    r1 = logchoose(m, X)
    try:
        r2 = logchoose(N-m, n-X)
    except ValueError:
        return 0
    r3 = logchoose(N, n)

    return exp(r1 + r2 - r3)


def hypergeo_cdf(X, n, m, N):
    """
    Returns the cummulative distribution function of drawing X successes of m marked items
    in n draws from a bin of N total items.

    :param X: number of successful draws
    :param n: number of draws
    :param m: number of marked items
    :param N: total number of items
    :return: cummulative distribution function
    """
    assert N >= m, 'Number of items %i must be larger than the number of marked items %i' % (N, m)
    assert m >= X, 'Number of marked items %i must be larger than the number of sucesses %i' % (m, X)
    assert n >= X, 'Number of draws %i must be larger than the number of sucesses %i' % (n, X)
    assert N >= n, 'Number of draws %i must be smaller than the total number of items %i' % (n, N)
    assert N-m >= n-X, 'There are more failures %i than unmarked items %i' % (N-m, n-X)

    s = 0
    for i in range(0, X+1):
        s += max(gauss_hypergeom(i, n, m, N), 0.0)
    return min(max(s, 0.0), 1)


def hypergeo_sf(X, n, m, N):
    """
    Returns the significance of drawing X successes of m marked items
    in n draws from a bin of N total items.

    :param X: number of successful draws
    :param n: number of draws
    :param m: number of marked items
    :param N: total number of items
    :return: significance
    """
    assert N >= m, 'Number of items %i must be larger than the number of marked items %i' % (N, m)
    assert m >= X, 'Number of marked items %i must be larger than the number of sucesses %i' % (m, X)
    assert n >= X, 'Number of draws %i must be larger than the number of sucesses %i' % (n, X)
    assert N >= n, 'Number of draws %i must be smaller than the total number of items %i' % (n, N)
    assert N-m >= n-X, 'There are more failures %i than unmarked items %i' % (N-m, n-X)

    s = 0
    for i in range(X, min(m, n)+1):
        s += max(gauss_hypergeom(i, n, m, N), 0.0)
    return min(max(s, 0.0), 1)


def rank_simple(vector):
    return sorted(range(len(vector)), key=vector.__getitem__)


def rankdata(a, method='average'):
    """

    source: http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python

    :param a:
    :return:
    """
    n = len(a)
    ivec=rank_simple(a)
    svec=[a[rank] for rank in ivec]
    sumranks = 0
    dupcount = 0
    newarray = [0]*n
    for i in range(n):
        sumranks += i
        dupcount += 1
        if i == n-1 or svec[i] != svec[i+1]:
            for j in range(i-dupcount+1,i+1):
                if method == 'average':
                    averank = sumranks / float(dupcount) + 1
                    newarray[ivec[j]] = averank
                elif method == 'max':
                    newarray[ivec[j]] = i+1
                elif method == 'min':
                    newarray[ivec[j]] = i+1 -dupcount+1
                else:
                    raise NameError('Unsupported method')

            sumranks = 0
            dupcount = 0

    return newarray


def fdr_correction(a):
    """
    applies fdr correction to a list of p-values

    :param a: list of p-values
    :return: list with adjusted/corrected p-values
    """
    ranks = rankdata(a, method='max')

    output = []

    for p, rank in zip(a, ranks):
        corrected = p * (len(a)/rank)
        output.append(corrected if corrected < max(a) else max(a))

    return output
