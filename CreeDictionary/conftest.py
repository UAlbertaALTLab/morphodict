import pytest
from django.conf import settings

# See “`conftest.py`: sharing fixtures across multiple files”
# https://docs.pytest.org/en/stable/fixture.html#conftest-py-sharing-fixtures-across-multiple-files


@pytest.fixture(scope="module")
def django_db_setup():
    """
    Normally pytest-django creates a new, empty in-memory database and runs
    all your migrations for you.

    You can override that behaviour by creating your own `django_db_setup`
    fixture: https://pytest-django.readthedocs.io/en/latest/database.html#django-db-setup

    We do so to reuse the same database file every time because:
      - there’s currently no mutation functionality in the app for which
        we need a clean database to test against
      - with the ~1400 entries in the test DB, it takes ~30 seconds to
        generate all the wordforms, which would be too long to wait every
        time you wanted to run a single unit test.

    If you want different behaviour for some tests, you can create your own
    django_db_setup fixture in a test file or per-directory conftest.py.

    And to get back the django default behaviour, simply do

        from pytest_django.fixtures import django_db_setup
        django_db_setup # reference so import doesn’t appear unused

    in a test or conftest.
    """

    # If this environment variable is set, a conditional in settings.py
    # should have pointed the database at CreeDictionary/test_db.sqlite3
    assert settings.USE_TEST_DB
