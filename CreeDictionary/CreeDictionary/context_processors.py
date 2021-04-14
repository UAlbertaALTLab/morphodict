"""
Django (template) context processors.
"""

from django.http import HttpRequest

from .display_options import DEFAULT_DISPLAY_MODE, DISPLAY_MODE_COOKIE, DISPLAY_MODES


def display_options(request: HttpRequest):
    """
    Django context processor that adds the "display" variable.
    "display" has the following attributes:

     - display.mode -- "community" or "linguistic"
    """
    return {"display_options": _DisplayOptions(request)}


class _DisplayOptions:
    """
    Provides the `display` template variable.
    """

    def __init__(self, request: HttpRequest):
        mode = request.COOKIES.get(DISPLAY_MODE_COOKIE)

        if mode not in DISPLAY_MODES:
            mode = DEFAULT_DISPLAY_MODE

        self.mode = mode
