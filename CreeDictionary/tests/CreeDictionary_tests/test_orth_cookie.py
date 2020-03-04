#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Test things involving the 'orth' cookie.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize("orth", ["Cans", "Latn", "Latn-x-macron"])
def test_can_set_orth_cookie(orth, client):
    """
    Test that POSTing to the URL actually sets the orthography.
    """
    # By default, there should be no orth cookie.
    index_url = reverse("cree-dictionary-index")
    response = client.get(index_url)
    assert response.status_code == 200
    assert "orth" not in response.cookies

    # Change the orthography!
    change_orth_url = reverse("cree-dictionary-change-orthography")
    response = client.post(change_orth_url, {"orth": orth})
    assert response.status_code in (200, 204)
    assert "orth" in response.cookies
    assert response.cookies["orth"].value == orth

    # The client should now set the orthography in its cookies.
    assert "orth" in client.cookies
    assert client.cookies["orth"].value == orth


@pytest.mark.parametrize("method", ["get", "head"])
def test_bad_methods(client, method):
    """
    We should not be able to GET or HEAD change-orthography URL.
    """

    change_orth_url = reverse("cree-dictionary-change-orthography")
    make_request = getattr(client, method)
    response = make_request(change_orth_url, {"orth": "Cans"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


# TODO: test invalid request
