"""
Makes it possible to read templates, static files, etc. for the crkeng dictionary.
"""

from django.apps import AppConfig


class CrkEngAppConfig(AppConfig):
    """
    itwêwina — the intelligent Plains Cree to English dictionary.

    This app config MUST **only** be regsitered in crkeng.site.settings
    """

    name = "crkeng"
    verbose_name = "itwêwina"
