import pytest
from django.test import Client
from django.urls import reverse


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
    # assert settings.USE_TEST_DB
    pass


@pytest.mark.django_db
def test_click_in_text_correct_usage():
    c = Client()

    # niskak means goose in plains Cree
    response = c.get(reverse("cree-dictionary-word-click-in-text-api")+"?q=niskak")

    assert b'goose' in response.content

@pytest.mark.django_db
def test_click_in_text_no_params():
    c = Client()

    response = c.get(reverse("cree-dictionary-word-click-in-text-api"))

    assert response.status_code == 400
