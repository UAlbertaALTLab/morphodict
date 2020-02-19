"""measure and report function execution time"""
import time
from functools import wraps
from typing import Callable, Any


def timed(
    msg: str = "{func_name} finished in {minute:02.0f}:{second:02.0f}",
) -> Callable[[Callable], Any]:
    """
    report the time a function consumes after the function finishes

    usage example: @timed(msg="the function took {second} seconds")

    :param msg: the message printed to stdout. "{func_name}", "{minute}" and "{second}" will be replaced
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
                    minute=total_seconds // 60,
                    second=total_seconds % 60,
                )
            )
            return result

        return timed_func

    return decorator
