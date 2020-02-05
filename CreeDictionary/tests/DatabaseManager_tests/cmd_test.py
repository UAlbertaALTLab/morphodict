import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import connection

from API.models import Wordform
from DatabaseManager.__main__ import cmd_entry
from DatabaseManager.cree_inflection_generator import expand_inflections


@pytest.fixture(scope="function")
def django_db_setup(django_db_blocker):
    """
    This works with pytest-django plugin.
    This fixture tells all functions marked with pytest.mark.django_db in this file to disable foreign_keys constraint

    Migration 0006 modifies database index and the default django_db_setup uses transaction to restore database after
    every test. As sqlite disallows schema modification while in transaction,
    the migration will error if foreign_keys constraint were set to true.
    """

    old_settings = settings.DATABASES
    settings.DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:",}
    }
    with django_db_blocker.unblock():
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        yield
        cursor.execute("PRAGMA foreign_keys = ON")

        call_command("flush", "--noinput")  # clear db
    settings.DATABASES = old_settings


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    cmd_entry([..., "import", str(shared_datadir / "crkeng-small-nice-0")])

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1
