#!/usr/bin/env python
"""
Command-line utility for administrative tasks.
"""

import os
import sys
from pathlib import Path

# sys.path[0] is initialized to the directory containing the script, which
# is too deep for our purposes.
sys.path[0] = os.fspath(Path(sys.path[0]).parent)

if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "CreeDictionary.CreeDictionary.settings"
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
