import logging
import os

from django.apps import AppConfig
from django.conf import settings

from CreeDictionary import cvd

logger = logging.getLogger(__name__)


class APIConfig(AppConfig):
    name = "CreeDictionary.API"

    def ready(self) -> None:
        # This function is called when you restart dev server or touch wsgi.py
        #
        # Avoid using this method. It gets called during startup of *every*
        # management command, wasting time, and when you’re running tests, the
        # database config inside this method can point at the production
        # database (!!)
        #
        # https://docs.djangoproject.com/en/3.1/ref/applications/#django.apps.AppConfig.ready
        #
        # For when you you really want eager loading:
        #   - The runserver auto-reloading sets a RUN_MAIN environment variable
        #   - Our wsgi.py sets PERFORM_TIME_CONSUMING_INITIALIZATIONS
        if (
            "RUN_MAIN" in os.environ
            or "PERFORM_TIME_CONSUMING_INITIALIZATIONS" in os.environ
        ):
            self.perform_time_consuming_initializations()

    def perform_time_consuming_initializations(self):
        from morphodict.search import affix
        from morphodict.lexicon.models import wordform_cache

        logger.debug("preloading caches")
        affix.cache.preload()
        wordform_cache.preload()
        if settings.MORPHODICT_ENABLE_CVD:
            cvd.preload_models()

        logger.debug("done")
