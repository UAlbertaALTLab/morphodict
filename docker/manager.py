#!/usr/bin/env python3

"""
docker-compose management code

Intended to handle things like:
  - Generating docker-compose YAML files
  - Making sure directories exist
  - Creating database files
  - Triggering a migration run
  - Getting a shell into a running container

This is all together in one script so that the configuration is consistent: the
YAML files point at the right places because they are both created by code that
ultimately gets their location from the same variable.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from docker_management.yaml import make_yaml
from docker_management.setup import do_privileged_setup


def main():
    parser = ArgumentParser()
    parser.formatter_class = ArgumentDefaultsHelpFormatter

    subparsers = parser.add_subparsers()
    subparsers.add_parser("make-yaml", help=make_yaml.__doc__).set_defaults(
        func=make_yaml
    )
    subparsers.add_parser(
        "privileged_setup", help=do_privileged_setup.__doc__
    ).set_defaults(func=do_privileged_setup)

    args = parser.parse_args()

    if "func" not in args:
        parser.error("No command specified")
    args.func(args)


if __name__ == "__main__":
    main()
