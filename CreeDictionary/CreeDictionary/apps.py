from django.apps import AppConfig


class CreeDictionaryConfig(AppConfig):
    name = "CreeDictionary"

    def ready(self):
        """
        initialize fuzzy search (build the data structure)
        """
        from django.db import connection

        if "API_inflection" in connection.introspection.table_names():
            # without the guard
            # on travis this line of code will be run before a database exist and will error
            from API.models import Inflection

            Inflection.init_fuzzy_searcher()
