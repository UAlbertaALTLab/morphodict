import argparse
import os
import sys
from argparse import ArgumentParser
from os import environ
from pathlib import Path

import django
from django.core.management import call_command


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = ArgumentParser(description="cli to manage django sqlite dictionary")

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

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CreeDictionary.settings")
    django.setup()

    from DatabaseManager.test_db_builder import build_test_xml
    from DatabaseManager.xml_importer import import_xmls
    from utils import shared_res_dir

    args = parser.parse_args(argv[1:])
    if args.command_name == "import":
        if args.wipe_first:
            call_command("wipedefinitions", yes_really=True)

        import_xmls(Path(args.xml_path))

    elif args.command_name == "build-test-db":
        assert (
            environ.get("USE_TEST_DB", "false").lower() == "true"
        ), "Environment variable USE_TEST_DB has to be True to create test_db.sqlite3"
        build_test_xml(args.process_count)
        import_xmls(
            shared_res_dir / "test_dictionaries",
            args.process_count,
        )
    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
