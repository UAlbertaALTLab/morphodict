# todo: command line
import argparse

from DatabaseManager.xml_consistency_checker import check_xml
from DatabaseManager.xml_importer import clear_database, import_crkeng_xml

parser = argparse.ArgumentParser(description="cli to manage django sqlite dictionary")

# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')
subparsers = parser.add_subparsers(dest="command_name")

clear_parser = subparsers.add_parser("clear", help="clear database")

import_parser = subparsers.add_parser("import", help="import from xml")

check_parser = subparsers.add_parser(
    "check", help="check the consistency of a xml source with the fst"
)
check_parser.add_argument("xml_filename")
check_parser.add_argument(
    "--verbose", "-v", action="store_true", help="whether gives omitted analysis"
)

import_parser.add_argument("xml_filename")

check_parser.add_argument(
    "--ambiguity",
    "-a",
    dest="check_only",
    action="store_const",
    const="ambiguity",
    help="only check for lemma - analysis ambiguities",
)

check_parser.add_argument(
    "--duplication",
    "-d",
    dest="check_only",
    action="store_const",
    const="duplication",
    help="only check for xml entry duplication (different <e> with the same lc and pos)",
)
# import_parser.add_parser('import', help='import from xml')

args = parser.parse_args()


if args.command_name == "clear":
    clear_database()
elif args.command_name == "import":
    import_crkeng_xml(args.xml_filename)
elif args.command_name == "check":
    check_xml(args.xml_filename, args.verbose, args.check_only)
