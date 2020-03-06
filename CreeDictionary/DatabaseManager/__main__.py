import argparse
import sys
from argparse import ArgumentParser
from os import environ, getcwd, chdir
from pathlib import Path
from typing import Union

from django.conf import settings
from django.core.management import call_command

from DatabaseManager.replace_db import create_replacing_migration
from DatabaseManager.test_db_builder import build_test_xml
from DatabaseManager.xml_importer import import_xmls
from utils import shared_res_dir


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

import_parser = subparsers.add_parser(
    "import",
    help="unlink existing .sqlite3 file, apply migrations from 0001 to 0005. "
    "Import from specified engcrk.xml and crkeng.xml. Migrate the rest",
)

replace_parser = subparsers.add_parser(
    "replace",
    help="Create a migration that builds a new database. The database is built as temporary_db.sqlite3 and "
    "renamed to db.sqlite3 when it's finished building",
)

build_test_db_parser = subparsers.add_parser(
    "build-test-db", help="build test_db.sqlite3 from res/test_db_words.txt"
)

add_multi_processing_argument(build_test_db_parser)

import_parser.add_argument(
    "xml_directory_name", help="The directory that has crkeng.xml and engcrk.xml"
)

for p in [build_test_db_parser, import_parser]:
    p.add_argument(
        "--noinput",
        "--no-input",
        dest="no_input",
        action="store_true",
        help="Do NOT interactively prompt the user anything",
    )
add_multi_processing_argument(import_parser)


def import_and_migrate(
    xml_dir_name: Union[Path, str], process_count: int, no_input=False
):
    """
    Unlink existing .sqlite3 file, apply migrations from API/0001 to API/0005
    Import from specified engcrk.xml and crkeng.xml. Then migrate all other migrations
    """
    if not no_input:
        user_in = input(
            f'this will DELETE database {settings.DATABASES["default"]["NAME"]}\n '
            "and create a new database from scratch.\n"
            "Are you sure? [y/N] "
        )
        if user_in.lower() != "y":
            print("Aborted")
            sys.exit(0)
    try:
        Path(settings.DATABASES["default"]["NAME"]).unlink()
    except FileNotFoundError:
        pass
    call_command("migrate", "API", "0005")
    import_xmls(Path(xml_dir_name), process_count)
    call_command("migrate")


def cmd_entry(argv=None):
    if argv is None:
        argv = sys.argv

    args = parser.parse_args(argv[1:])
    if args.command_name == "import":
        import_and_migrate(args.xml_directory_name, args.process_count, args.no_input)
    elif args.command_name == "build-test-db":
        assert (
            environ.get("USE_TEST_DB", "false").lower() == "true"
        ), "Environment variable USE_TEST_DB has to be True to create test_db.sqlite3"
        build_test_xml(args.process_count)
        import_and_migrate(
            shared_res_dir / "test_dictionaries",
            args.process_count,
            no_input=args.no_input,
        )
    elif args.command_name == "replace":
        create_replacing_migration()
    else:
        raise NotImplementedError


if __name__ == "__main__":
    cmd_entry(argv=sys.argv)
