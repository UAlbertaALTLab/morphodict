"""
Django (template) context processors.
"""

from django.http import HttpRequest

from .display_options import DEFAULT_DISPLAY_MODE, DISPLAY_MODE_COOKIE, DISPLAY_MODES


def display(request: HttpRequest):
    """
    Django context processor that augments the context with "display". "display" has the
    following:

     - display.mode -- "basic" or "traditional"
    """
    return {"display": _Display(request)}


class _Display:
    """
    Provides the `display` template variable.
    """

    def __init__(self, request: HttpRequest):
        mode = request.COOKIES.get(DISPLAY_MODE_COOKIE)

        if mode not in DISPLAY_MODES:
            mode = DEFAULT_DISPLAY_MODE

        self.mode = mode