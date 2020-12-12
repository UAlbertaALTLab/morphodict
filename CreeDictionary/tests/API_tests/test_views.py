import time

import pytest
from django.conf import settings
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
    assert settings.USE_TEST_DB


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


class TestClickInTextDisablesAffixSearch:
    """
    This test is a comparison
    #  1. Normal searching with wapamew and affix search on should yield asawâpamêw
    #  2. click in text search won't yield asawâpamêw
    """

    ASCII_WAPAMEW = "wapamew"
    EXPECTED_SUFFIX_SEARCH_RESULT = "asawâpamêw"

    @pytest.mark.django_db
    def test_normal_search_uses_affix_search(self):
        c = Client()
        normal_search_response = c.get(
            reverse("cree-dictionary-search") + f"?q={self.ASCII_WAPAMEW}"
        ).content.decode("utf-8")
        assert self.EXPECTED_SUFFIX_SEARCH_RESULT in normal_search_response

    @pytest.mark.django_db
    def test_click_in_text_disables_affix_search(self):
        c = Client()
        click_in_text_response = c.get(
            reverse("cree-dictionary-word-click-in-text-api")
            + f"?q={self.ASCII_WAPAMEW}"
        ).content.decode("utf-8")
        assert self.EXPECTED_SUFFIX_SEARCH_RESULT not in click_in_text_response

    # Note the class pattern with *two methods* is deliberate here.
    # You might be tempted to use a single function instead as below:
    # This however won't work. I (Matt Yan <syan4.ualberta.ca>) spent great time on this.
    # You'll see "sqliteError: Cannot operate on a closed database" during the second client.get()
    # It seems like something closes the database connection after the first client.get()
    # And I can't find related bug/issue reports on the web
    # The moral is, whenever you need multiple client.get()'s, split into multiple function

    # Think positively too! The above class pattern is so much more readible and clearer!

    # @pytest.mark.django_db
    # def test_click_in_text_no_affix_search():
    #
    #     c = Client() # tried: seperate client instances c1, c2 won't help
    #
    #     ascii_wapamew = "wapamew"
    #     suffix_search_result = "asawâpamêw"
    #
    #     normal_search_response = c.get(reverse("cree-dictionary-search") + f"?q={ascii_wapamew}").content.decode("utf-8")
    #     click_in_text_response = c.get(
    #         reverse("cree-dictionary-word-click-in-text-api") + f"?q={ascii_wapamew}").content.decode(
    #         "utf-8")
    #     assert suffix_search_result in normal_search_response and suffix_search_result not in click_in_text_response
