from functools import cache


def cache_unless(arg: bool, /):
    """
    Conditional version of @functools.cache.

    Will only cache the results if `arg` is True.

    Sample usage:

        @cache_unless(settings.DEBUG)
        def expensive_thing():
            ...
    """
    if arg:
        return lambda x: x
    return cache
