import argparse
from argparse import ArgumentParser
import sys
from distutils.util import strtobool
from os import environ
from pathlib import Path

from DatabaseManager.xml_importer import clear_database, import_xmls


def add_multi_processing_argument(ap: ArgumentParser):
    ap.add_argument(
        "--multi-processing",
        "-m",
        dest="process_count",
        type=int,
        action="store",
        default=1,
        help="Use multi-processing to accelerate import. Default is 1, which is no multi-processing. "
        "A rule is to use as many processes as the number of cores in the machine.",
    )


parser = argparse.ArgumentParser(description="cli to manage django sqlite dictionary")

subparsers = parser.add_subparsers(dest="command_name")
subparsers.required = True

clear_parser = subparsers.add_parser(
    "clear",
    help="clear imported dictionary from database. (superuser data will be kepted)",
)

import_parser = subparsers.add_parser(
    "import", help="import from xml. Old dictionary data will be CLEARED"
)

build_test_db_parser = subparsers.add_parser(
    "build-test-db", help="build test_db.sqlite3 from res/test_db_words.txt"
)
add_multi_processing_argument(build_test_db_parser)

import_parser.add_argument(
    "xml_directory_name", help="The directory that has crkeng.xml and engcrk.xml"
)

add_multi_processing_argument(import_parser)


def cmd_entry(argv=sys.argv):
    args = parser.parse_args(argv[1:])
    if args.command_name == "clear":
        clear_database()
    elif args.command_name == "import":
        import_xmls(Path(args.xml_directory_name), args.process_count)
    elif args.command_name == "build-test-db":
        assert (
            strtobool(environ.get("USE_TEST_DB", "false")) is True
        ), "Environment variable USE_TEST_DB has to be True to create test_db.sqlite3"
        pass


if __name__ == "__main__":
    cmd_entry(argv=sys.argv)
