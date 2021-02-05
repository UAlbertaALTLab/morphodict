import pytest
from django.conf import settings
from django.urls import reverse

from API.models import Wordform


@pytest.fixture(scope="module")
def django_db_setup():
    """
    This works with pytest-django plugin.
    This fixture tells all functions marked with pytest.mark.django_db in this file
    to use the database specified in settings.py
    which is the existing test_db.sqlite3 if USE_TEST_DB=True is passed.

    Instead of by default, an empty database in memory.
    """

    # all functions in this file should use the existing test_db.sqlite3
    assert settings.USE_TEST_DB


@pytest.mark.django_db
def test_admin_doesnt_crash(admin_client):
    "This is a minimal test that we can view a wordform in the admin interface"
    one_wordform = Wordform.objects.filter(is_lemma=True).first()
    response = admin_client.get(
        reverse("admin:API_wordform_change", args=[one_wordform.id])
    )
    assert response.status_code == 200
    assert b"Inflections" in response.content
