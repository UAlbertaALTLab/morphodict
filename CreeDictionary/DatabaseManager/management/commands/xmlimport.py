from argparse import ArgumentParser
from pathlib import Path

from django.core.management import BaseCommand, call_command

from CreeDictionary.ensure_data import ensure_wordform_paradigms


class Command(BaseCommand):
    help = """Import a dictionary .xml file into db search tables.

    At a high level, this will (1) analyze each wordform to get a lemma, then
    (2) generate all wordforms of the lemmas. During this process, definitions
    are associated with wordforms, and are also stemmed to allow searching.
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

    def handle(self, *args, **options):
        from DatabaseManager.xml_importer import import_xmls

        if options["command_name"] == "import":
            if options["wipe_first"]:
                call_command("wipedefinitions", yes_really=True)

            import_xmls(Path(options["xml_path"]))
            # As of 2021-05-10, the XML format does not specify explicit paradigm fields
            # for, e.g., demonstrative pronouns or personal pronouns, so add them in
            # here:
            ensure_wordform_paradigms()
        else:
            raise NotImplementedError
