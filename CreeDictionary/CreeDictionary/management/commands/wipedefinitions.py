from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.db import connection

from API.models import Definition, DictionarySource, EnglishKeyword, Wordform


class Command(BaseCommand):
    help = """Erase all rows from all definition-related database tables.

    This is useful to run before importing a new dictionary.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--yes-really", default=False, action="store_true")

    def handle(self, *args, **options):
        if not options["yes_really"]:
            self.stdout.write("Showing status only. Counts of what would be deleted:")

        # The order matters due to foreign keys
        for model in [
            EnglishKeyword,
            Definition.citations.through,
            Definition,
            Wordform,
            DictionarySource,
        ]:
            self.stdout.write(f"{model.__name__}: {model.objects.count():,}")

            if options["yes_really"]:
                cursor = connection.cursor()
                cursor.execute(f"DELETE FROM {model._meta.db_table}")
