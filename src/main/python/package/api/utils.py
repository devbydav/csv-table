from time import perf_counter

import logging

logger = logging.getLogger(__name__)


def log_time_it(func):
    def timed(*args, **kw):
        t0 = perf_counter()
        res = func(*args, **kw)
        t1 = perf_counter()
        logger.info(f"{func.__name__} run in {round(t1-t0, 5)}")
        return res
    return timed
