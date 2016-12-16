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

        args_str = (str(args)[:75] + ' ... ') if len(str(args)) > 75 else str(args)

        print('%r: started: %2.3f, ran: %2.3f sec' % (method.__name__, ts,  te-ts))
        return result

    return timed
