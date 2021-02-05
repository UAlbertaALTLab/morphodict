import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = """Erase all rows from all definition-related database tables.

    This is useful to run before importing a new dictionary.
    """

    def add_arguments(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(dest="command_name")
        subparsers.required = True

        import_parser = subparsers.add_parser(
            "import",
            help="Import from specified crkeng.xml. This assumes the database is at migration 0001",
        )
        import_parser.add_argument(
            "xml_path", help="The XML file, or directory containing crkeng*.xml"
        )
        import_parser.add_argument("--wipe-first", action="store_true")

        subparsers.add_parser(
            "build-test-db", help="build test_db.sqlite3 from res/test_db_words.txt"
        )

    def handle(self, *args, **options):
        from DatabaseManager.test_db_builder import build_test_xml
        from DatabaseManager.xml_importer import import_xmls
        from utils import shared_res_dir

        if options["command_name"] == "import":
            if options["wipe_first"]:
                call_command("wipedefinitions", yes_really=True)

            import_xmls(Path(options["xml_path"]))

        elif options["command_name"] == "build-test-db":
            assert (
                os.environ.get("USE_TEST_DB", "false").lower() == "true"
            ), "Environment variable USE_TEST_DB has to be True to create test_db.sqlite3"
            build_test_xml()
            import_xmls(shared_res_dir / "test_dictionaries")
        else:
            raise NotImplementedError
