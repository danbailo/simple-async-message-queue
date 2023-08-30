import asyncio

from functools import wraps

import time

from .logger import logger


def async_timeit(f):
    @wraps(f)
    def async_timeit(*args, **kwargs):
        start = time.monotonic()
        try:
            return asyncio.run(f(*args, **kwargs))
        finally:
            logger.info(
                f'time elapsed to run "{f.__name__}"'
                f' - {time.monotonic() - start:0.2f}s'
            )
    return async_timeit


def timeit(f):
    @wraps(f)
    def timeit(*args, **kwargs):
        start = time.monotonic()
        try:
            return f(*args, **kwargs)
        finally:
            logger.info(
                f'time elapsed to run "{f.__name__}"'
                f' - {time.monotonic() - start:0.2f}s'
            )
    return timeit
