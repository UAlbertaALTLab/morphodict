# type: ignore # mypy thinks the dynamically-returned Runserver class is not
# valid as a base class.
"""
This repo contains multiple django sites. To allow developers to more easily run
several of them at once, we extend the default runserver command to optionally
take its default port from settings.
"""
from django.conf import settings
from django.core.servers.basehttp import WSGIServer

from morphodict.runserver.get_next_runserver import get_next_runserver_command

Runserver = get_next_runserver_command(__name__)


class TriggeringWSGIServer(WSGIServer):
    def serve_forever(self, *args, **kwargs):
        import swiftpy

        print("sending serve trigger")
        swiftpy.trigger("serve")

        super().serve_forever(*args, **kwargs)


def get_default_port():
    if hasattr(settings, "DEFAULT_RUNSERVER_PORT"):
        return settings.DEFAULT_RUNSERVER_PORT
    return 8000


class Command(Runserver):
    default_port = get_default_port()

    def add_arguments(self, parser):
        parser.add_argument(
            "--swiftpy-trigger",
            default=False,
            help="Whether to send a swiftpy ‘serve’ trigger on serve start",
        )
        super().add_arguments(parser)

    def handle(self, swiftpy_trigger, *args, **kwargs):
        if swiftpy_trigger:
            Command.server_cls = TriggeringWSGIServer
        super().handle(*args, **kwargs)
