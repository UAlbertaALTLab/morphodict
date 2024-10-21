"""
Test things involving the 'orth' cookie.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse

from morphodict.orthography import ORTHOGRAPHY


@pytest.mark.parametrize(
    "orth", ["Cans", "Latn", "Latn-x-macron", "Latn-y", "Latn-x-macron-y"]
)
def test_can_set_orth_cookie(orth, client, change_orth_url):
    """
    Test that POSTing to the URL actually sets the orthography.
    """
    # By default, there should be no orth cookie.
    index_url = reverse("cree-dictionary-index")
    response = client.get(index_url)
    assert response.status_code == 200
    assert ORTHOGRAPHY.COOKIE_NAME not in response.cookies

    # Change the orthography!
    response = client.post(change_orth_url, {"orth": orth})
    assert response.status_code in (200, 204)
    assert ORTHOGRAPHY.COOKIE_NAME in response.cookies
    assert response.cookies[ORTHOGRAPHY.COOKIE_NAME].value == orth

    # The client should now set the orthography in its cookies.
    assert ORTHOGRAPHY.COOKIE_NAME in client.cookies
    assert client.cookies[ORTHOGRAPHY.COOKIE_NAME].value == orth


@pytest.mark.parametrize("method", ["get", "head"])
def test_bad_methods(method, client, change_orth_url):
    """
    We should not be able to GET or HEAD change-orthography URL.
    """
    make_request = getattr(client, method)
    response = make_request(change_orth_url, {"orth": "Cans"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_bad_orthography(client, change_orth_url):
    """
    Test changing the orthography to an invalid value.
    """
    response = client.post(change_orth_url, {"orth": "syllabics"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_no_orthography(client, change_orth_url):
    """
    Test POSTing with no query arguments.
    """
    response = client.post(change_orth_url, {})
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.fixture
def change_orth_url():
    return reverse("morphodict.orthography:change-orthography")
