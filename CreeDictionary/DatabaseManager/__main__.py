# todo: command line
import argparse

from DatabaseManager.xml_importer import clear_database, import_crkeng_xml

parser = argparse.ArgumentParser(description="cli to manage django sqlite dictionary")

subparsers = parser.add_subparsers(dest="command_name")

clear_parser = subparsers.add_parser(
    "clear",
    help="clear imported dictionary from database. (superuser data will be kepted)",
)

import_parser = subparsers.add_parser(
    "import", help="import from xml. Old dictionary data will be CLEARED"
)


import_parser.add_argument("xml_filename")

import_parser.add_argument(
    "--multi-processing",
    "-m",
    dest="process_count",
    type=int,
    action="store",
    default=1,
    help="Use multi-processing to accelerate import. Default is 1, which is no multi-processing. A rule is to use as many processes as the number of cores of the machine.",
)


args = parser.parse_args()


if args.command_name == "clear":
    clear_database()
elif args.command_name == "import":
    import_crkeng_xml(args.xml_filename, args.process_count)
