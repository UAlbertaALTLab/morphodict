# todo: command line
import argparse

from DatabaseManager.xml_importer import clear_database

parser = argparse.ArgumentParser(description='cli to manage django sqlite dictionary')

# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')

parser.add_argument('command', choices=('clear', 'import'))

args = parser.parse_args()


if args.command == 'clear':
    clear_database()