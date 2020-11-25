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
    response = c.get(reverse("cree-dictionary-word-click-in-text-api") + "?q=niskak")

    assert b"goose" in response.content


@pytest.mark.django_db
def test_click_in_text_no_params():
    c = Client()

    response = c.get(reverse("cree-dictionary-word-click-in-text-api"))

    assert response.status_code == 400


@pytest.mark.django_db
def test_click_in_text_no_affix_search():
    # This test guarantees affix search is turned off in click-in-text API

    # Should affix search be turned on for click-in-tex, we would have a full page of results
    # for the case of wapamew and a lot of results are from prefix/suffix search
    #
    # The user might not be certain what they are looking for on Itwewina, thus the need
    # for relaxation and affix search. While click-in-text users searches for some exact cree they find on the web.
    # So prefix/suffix search is unnecessary.
    c = Client()

    ascii_wapamew = "wapamew"
    suffix_search_result = "asawâpamêw"
    normal_search_response = c.get(reverse("cree-dictionary-search") + f"?q={ascii_wapamew}").content.decode("utf-8")
    click_in_text_response = c.get(reverse("cree-dictionary-word-click-in-text-api") + f"?q={ascii_wapamew}").content.decode(
        "utf-8")

    assert suffix_search_result in normal_search_response and suffix_search_result not in click_in_text_response
