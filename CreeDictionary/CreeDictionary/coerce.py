#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from typing import Union


def to_boolean(envvar: Union[str, bool]) -> bool:
    """
    Coerce the input to a boolean.

    >>> to_boolean("True")
    True
    >>> to_boolean("FALSE")
    False

    NOTE: An empty string is interpreted as False:

    >>> to_boolean("")
    False

    Booleans are returned as-is:

    >>> to_boolean(True)
    True
    >>> to_boolean(False)
    False

    Anything else is an error:

    >>> to_boolean("1")
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce value to True or False: '1'
    """
    if isinstance(envvar, bool):
        return envvar

    str_value = envvar.lower()
    if str_value == "true":
        return True
    elif str_value in ("false", ""):
        return False
    else:
        raise ValueError(f"Could not coerce value to True or False: {envvar!r}")
