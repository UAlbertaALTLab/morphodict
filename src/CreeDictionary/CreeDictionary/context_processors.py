"""
Django (template) context processors.
"""

from django.http import HttpRequest

from crkeng.app.preferences import DisplayMode


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
        mode = request.COOKIES.get(DisplayMode.cookie_name)

        if mode not in DisplayMode.choices:
            mode = DisplayMode.default

        self.mode = mode
