from contextlib import contextmanager

import pytest
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_databases, teardown_databases
from pytest_django.lazy_django import get_django_version

from CreeDictionary.DatabaseManager.xml_importer import import_xmls


@contextmanager
def no_migration():
    """
    makes migrations temporarily not visible.
    """

    # adapted from fixtures.py in pytest-django

    from django.conf import settings
    from django.core.management.commands import migrate

    class DisableMigrations:
        def __init__(self):
            self._django_version = get_django_version()

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    class MigrateSilentCommand(migrate.Command):
        def handle(self, *args, **kwargs):
            kwargs["verbosity"] = 0
            return super(MigrateSilentCommand, self).handle(*args, **kwargs)

    old_modules = settings.MIGRATION_MODULES
    old_command = migrate.Command

    settings.MIGRATION_MODULES = DisableMigrations()
    migrate.Command = MigrateSilentCommand

    yield

    settings.MIGRATION_MODULES = old_modules
    migrate.Command = old_command


@pytest.fixture(scope="function")
def django_db_setup(request, django_test_environment, django_db_blocker):
    """
    This works with pytest-django plugin.

    The default django_db_setup fixture creates empty in-memory database and apply migrations at start of test session

    This fixture overrides the default django_db_setup fixture for the functions under current directory.
    It tells all functions marked with pytest.mark.django_db in this file to not automatically migrate
    database while setting up, create an empty database instead. So that we can test xml-importing
    related functions which apply migration and create database manually
    """

    # this fixture is adapted from that in fixtures.py in pytest-django.
    # It's the recommended practice from pytest-django.
    # See https://pytest-django.readthedocs.io/en/latest/database.html#fixtures

    with django_db_blocker.unblock():
        with no_migration():
            db_cfg = setup_databases(
                verbosity=request.config.option.verbose, interactive=False
            )

            # disable foreign_keys constraint for the database
            #
            # pytest_django uses transaction to restore database after every test function
            # As sqlite disallows schema modification in transaction when foreign keys constraints are enabled,
            # and our migrations have schema modification in them (e.g. creation of indexes in 0006)
            # the migration would error if foreign_keys constraint were set to ON.
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF")
            # drop tables so that we can test creating them from start
            for delete_from in call_command("sqlflush", verbosity=0).splitlines()[1:-1]:
                if "API_" in delete_from:
                    cursor.execute(
                        delete_from.replace("DELETE FROM", "DROP TABLE IF EXISTS")
                    )

        call_command("migrate", "--fake", "API", "zero")

    def teardown_database():
        with django_db_blocker.unblock():
            try:
                teardown_databases(db_cfg, verbosity=request.config.option.verbose)
            except Exception as exc:
                request.node.warn(
                    pytest.PytestWarning(
                        "Error when trying to teardown test databases: %r" % exc
                    )
                )

    request.addfinalizer(teardown_database)


def migrate_and_import(dictionary_dir):
    """
    assuming a fresh in memory database
    Do the initial migration and import the xml
    """
    call_command("migrate", "API")
    import_xmls(dictionary_dir)
