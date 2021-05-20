"""
Makes it possible to read templates, static files, etc. for the crkeng dictionary.
"""
import os
from pathlib import Path

from django.apps import AppConfig


class CrkEngAppConfig(AppConfig):
    """
    itwêwina — the intelligent Plains Cree to English dictionary.

    This app config MUST **only** be regsitered in crkeng.site.settings
    """

    name = "crkeng"
    verbose_name = "itwêwina"

    # Look for application files in the containing directory of this file.
    # (Django tries to guess this, but guesses wrong).
    path = os.fspath(Path(__file__).resolve().parent)
