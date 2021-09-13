import os
import sys
import threading
from io import IOBase

import django
from django.core.management import call_command

import morphodict_mobile


def setup_logging():
    """Redirect python stdout+stderr to iOS system log

    This adds timestamps during development, and allows python output to be
    collected later from a device that wasn’t hooked up to Xcode at the time, by
    running `sudo log collect --device`
    """

    class Log(IOBase):
        def __init__(self, name):
            self.name = name

        def write(self, s):
            if not isinstance(s, str):
                s = str(s)
            if s.strip():
                morphodict_mobile.log(self.name + ": " + s)

    sys.stdout = Log("pystdout")
    sys.stderr = Log("pystderr")


setup_logging()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crkeng.site.settings")

# Save a bit of memory by giving runserver threads 1MiB stacks instead of
# default 8MiB.
threading.stack_size(1024 * 1024)

django.setup()

call_command("runserver", use_reloader=False, addrport="4828", mobile_trigger=True)
