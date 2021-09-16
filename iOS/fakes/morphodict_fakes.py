def unavailable(*args, **kwargs):
    """A fake function that raises an error if you try to call it."""
    raise NotImplementedError()


class _MetaUnavailable(type):
    """
    A metaclass that prevents accessing class attributes.
    """

    def __getattribute__(self, item):
        raise NotImplementedError()


class Unavailable(metaclass=_MetaUnavailable):
    """A fake class that raises an error if you try to do anything with it.

    The constructor throws an error, and attempts to access class properties
    will also fail.
    """

    def __init__(self):
        raise NotImplementedError()

    def __getattribute__(self, item):
        raise NotImplementedError()
