#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from http import HTTPStatus

import pytest
from CreeDictionary.utils import url_for_query
from django.urls import reverse


@pytest.mark.django_db
def test_redirect(client):
    wordform = "wâpamêw"
    response = client.get(reverse("cree-dictionary-index-with-query", args=[wordform]))
    assert (
        response.status_code == HTTPStatus.MOVED_PERMANENTLY
    ), "Did not get a redirect"

    # Ensure the redirect is for the correct query.
    assert url_for_query(wordform) in response.url
