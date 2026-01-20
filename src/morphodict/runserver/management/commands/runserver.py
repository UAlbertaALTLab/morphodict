# type: ignore # mypy thinks the dynamically-returned Runserver class is not
# valid as a base class.
"""
This repo contains multiple django sites. To allow developers to more easily run
several of them at once, we extend the default runserver command to optionally
take its default port from settings.
"""

from argparse import BooleanOptionalAction

from django.conf import settings
from django.core.management.commands import runserver
from django.core.servers.basehttp import WSGIServer

from morphodict.runserver.get_next_runserver import get_next_runserver_command
from morphodict.runserver.mobile_run_handler import custom_run

Runserver = get_next_runserver_command(__name__)


class TriggeringWSGIServer(WSGIServer):
    """A WSGIServer extension that fires a trigger on startup

    Used to wait until the server is running before trying to load the home page
    in the mobile app.
    """

    def serve_forever(self, *args, **kwargs):
        import morphodict_mobile

        print("sending serve trigger")
        morphodict_mobile.trigger("serve")

        super().serve_forever(*args, **kwargs)


def get_default_port():
    if hasattr(settings, "DEFAULT_RUNSERVER_PORT"):
        return settings.DEFAULT_RUNSERVER_PORT
    return 8000


class Command(Runserver):
    default_port = get_default_port()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "--mobile-trigger",
            action=BooleanOptionalAction,
            default=False,
            help="Whether to send a ‘serve’ trigger for the mobile app on serve start",
        )
        super().add_arguments(parser)

    def handle(self, mobile_trigger, *args, **kwargs):
        if mobile_trigger:
            Command.server_cls = TriggeringWSGIServer
            runserver.run = custom_run
        super().handle(*args, **kwargs)
