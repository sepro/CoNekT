import time
from functools import wraps


def benchmark(method):
    """
    Benchmark decorator, a quick and convenient way to time a function

    :param method: function it wraps
    :return: decorated function
    """
    @wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts))
        return result

    return timed
