"""measure and report function execution time"""
import time
from functools import wraps
from typing import Callable, Any


def timed(
    msg: str = "function {func_name} took {minute}:{second}",
) -> Callable[[Callable], Any]:
    """
    usage example: @timed(msg="the function took {second} seconds")

    :param msg: the message printed to stdout. "{func_name}", "{minute}" and "{second}"
        will be replaced to real time consumption
    """

    def decorator(function: Callable,):
        @wraps(function)
        def timed_func(*args, **kw):
            ts = time.time()
            result = function(*args, **kw)
            te = time.time()
            total_seconds = te - ts
            print(
                msg.format(
                    func_name=function.__name__,
                    minute=round(total_seconds // 60),
                    second=round(total_seconds % 60),
                )
            )
            return result

        return timed_func

    return decorator
