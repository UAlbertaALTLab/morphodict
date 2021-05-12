import logging
import os

from django.apps import AppConfig, apps

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
        from CreeDictionary.API.models import wordform_cache
        from CreeDictionary.API.search import affix

        logger.debug("preloading caches")
        affix.cache.preload()
        wordform_cache.preload()
        cvd.preload_models()

        logger.debug("done")

    @classmethod
    def active_instance(cls) -> "APIConfig":
        """
        Fetch the instance of this Config from the Django app registry.

        This way you can get access to the affix searchers in other modules!
        """
        return apps.get_app_config(cls.name)
