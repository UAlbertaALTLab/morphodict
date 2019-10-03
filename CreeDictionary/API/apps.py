from django.apps import AppConfig
from django.db import connection


class APIConfig(AppConfig):
    name = "API"

    def ready(self):
        """
        initialize fuzzy search (build the data structure)
        """

        # without the guard
        # on travis this line of code will be run before a database exist and will error
        if "API_inflection" in connection.introspection.table_names():
            # Have to do it locally, or will get error (apps aren't loaded yet)
            from API.models import Inflection

            Inflection.init_fuzzy_searcher()
