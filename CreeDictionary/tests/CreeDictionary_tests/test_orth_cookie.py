#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Test things involving the 'orth' cookie.
"""

from django.urls import reverse


def test_can_set_orth_cookie(client):
    orth = "Cans"

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


# TODO: test invalid request
