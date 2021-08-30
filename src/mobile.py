import os
import threading

import django
from django.core.management import call_command

print("Hello, world")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crkeng.site.settings")
# Would be nice, but need to migrate first
# os.environ.setdefault("PERFORM_TIME_CONSUMING_INITIALIZATIONS", "True")

import swiftpy

swiftpy.trigger("hello")

# Save a bit of memory by giving runserver threads 1MiB stacks instead of
# default 8MiB.
threading.stack_size(1024 * 1024)

django.setup()

call_command("runserver", use_reloader=False, addrport="4828", swiftpy_trigger=True)
