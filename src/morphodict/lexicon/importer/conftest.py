from django.db import transaction
from django.core.management import call_command
import pytest


# Make sure we are using the default in-memory database setup for import tests.


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_blocker):
    with django_db_blocker.unblock():
        # atomic transaction lets us rollback the status of the database once done.
        with transaction.atomic():
            # flush command empties the database for purposes of this module.
            call_command("flush", verbosity=0, interactive=False)
            yield
            transaction.set_rollback(True)
