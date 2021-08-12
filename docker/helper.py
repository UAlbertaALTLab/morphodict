#!/usr/bin/env python3

"""
Helper script for dealing with docker-compose

Handles things like:
  - Generating docker-compose YAML files
  - Making sure directories exist
  - Running migrations
  - Getting a shell into a running container
"""

# This is all together in one program so that the configuration is consistent:
# the YAML files point at the right places because they are both created by code
# that ultimately gets their location from the same variable.

import argparse
import itertools
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os import fspath, execvp, chdir

from helpers.settings import DOCKER_COMPOSE_DIR, APPS
from helpers.setup import do_setup
from helpers.yaml import make_yaml


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    if "func" not in args:
        parser.error("No command specified")
    args.func(args)


def create_argument_parser():
    parser = ArgumentParser(description=__doc__)
    parser.formatter_class = ArgumentDefaultsHelpFormatter

    subparsers = parser.add_subparsers()

    def add_subparser(name, command):
        subparser = subparsers.add_parser(name, help=command.__doc__)
        subparser.set_defaults(func=command)
        return subparser

    def add_container_arg(subparser, allow_all=False):
        choices = [app.name for app in APPS]
        if allow_all:
            choices += ["all"]

        subparser.add_argument("container", choices=choices)
        return subparser

    add_subparser("make-yaml", make_yaml)
    add_subparser("setup", do_setup)

    add_container_arg(add_subparser("shell", shell))

    manage_subparser = add_container_arg(
        add_subparser("manage", manage), allow_all=True
    )
    manage_subparser.add_argument("manage_args", nargs=argparse.REMAINDER)

    staging_subparser = add_subparser("staging", staging)
    staging_subparser.add_argument("compose_args", nargs=argparse.REMAINDER)

    return parser


def shell(args):
    """Enter a shell for the given container

    The container must already be running via `docker-compose up`.
    """
    chdir(DOCKER_COMPOSE_DIR)
    execvp(
        "docker-compose",
        [
            "docker-compose",
            "-f",
            fspath(DOCKER_COMPOSE_DIR / "docker-compose.yml"),
            "exec",
            args.container,
            "/bin/bash",
        ],
    )


def manage(args):
    """Run django manage commands for the given container(s).

    The containers must already be running via `docker-compose up`.
    """
    containers = [args.container]
    if args.container == "all":
        containers = [app.name for app in APPS]

    for container in containers:

        app = next(app for app in APPS if app.name == container)

        if len(containers) > 1:
            print(f"Running {app.name}-manage")

        subprocess.check_call(
            [
                "docker-compose",
                "-f",
                fspath(DOCKER_COMPOSE_DIR / "docker-compose.yml"),
                "exec",
                "-T",
                container,
                f"/app/{app.name}-manage",
            ]
            + args.manage_args,
            # This could be specified as --project-directory, but then there are
            # issues with .env file finding, which is used to set
            # COMPOSE_PROJECT_NAME. The docs suggest these issues were dealt
            # with in docker-compose v1.28+, but that’s not yet in any released
            # Ubuntu version.
            cwd=DOCKER_COMPOSE_DIR,
        )


def staging(args):
    """
    Run `docker-compose` against the staging compose files.

    Also includes a local `docker-compose.override.yml` if it exists.

    Saves typing vs adding all the `-f ...` args by hand.
    """
    additional_compose_files = []

    local_override = DOCKER_COMPOSE_DIR / "docker-compose.override.yml"
    if local_override.exists():
        additional_compose_files.append(local_override)

    # not using more_itertools because want this part of the script to work even
    # without a working pipenv
    flatten = itertools.chain.from_iterable

    subprocess.check_call(
        [
            "docker-compose",
            "--project-name",
            "morphodict-staging",
            "-f",
            fspath(DOCKER_COMPOSE_DIR / "docker-compose.yml"),
            "-f",
            fspath(DOCKER_COMPOSE_DIR / "docker-compose.staging-override.yml"),
            *flatten(["-f", f] for f in additional_compose_files),
            *args.compose_args,
        ],
        cwd=DOCKER_COMPOSE_DIR,
    )


if __name__ == "__main__":
    main()
