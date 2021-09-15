def unavailable(*args, **kwargs):
    raise NotImplementedError()


class Unavailable:
    def __init__(self):
        raise NotImplementedError()

    def __getattr__(self, item):
        raise NotImplementedError()
