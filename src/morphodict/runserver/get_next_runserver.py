# This file contains a modified version of
# https://github.com/evansd/whitenoise/blob/master/whitenoise/runserver_nostatic/management/commands/runserver.py
# which is distributed under the following license:
#
# The MIT License (MIT)
#
# Copyright (c) 2013 David Evans
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Subclass the existing 'runserver' command.

There is some unpleasant hackery here because we don't know which command class
to subclass until runtime as it depends on which INSTALLED_APPS we have, so we
have to determine this dynamically.
"""

from importlib import import_module

from django.apps import apps


def get_next_runserver_command(module_name):
    """
    Return the next highest priority "runserver" command class
    """
    for app_name in _get_lower_priority_apps(module_name):
        module_path = "%s.management.commands.runserver" % app_name
        try:
            return import_module(module_path).Command
        except (ImportError, AttributeError):
            pass
    raise Exception("No runserver command found.")


def _get_lower_priority_apps(module_name):
    """
    Yield all app module names below the current app in the INSTALLED_APPS list
    """
    self_app_name = ".".join(module_name.split(".")[:-3])
    reached_self = False
    for app_config in apps.get_app_configs():
        if app_config.name == self_app_name:
            reached_self = True
        elif reached_self:
            yield app_config.name
    yield "django.core"
