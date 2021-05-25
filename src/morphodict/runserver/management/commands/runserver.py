"""
This repo contains multiple django sites. To allow developers to more easily run
several of them at once, we extend the default runserver command to optionally
take its default port from settings.
"""
from django.conf import settings

from morphodict.runserver.get_next_runserver import get_next_runserver_command

Runserver = get_next_runserver_command(__name__)


def get_default_port():
    if hasattr(settings, "DEFAULT_RUNSERVER_PORT"):
        return settings.DEFAULT_RUNSERVER_PORT
    return 8000


class Command(Runserver):
    default_port = get_default_port()
