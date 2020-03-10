#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_redirect(client):
    lemma = "wâpamêw"
    response = client.get(reverse("cree-dictionary-index-with-query", args=[lemma]))
    assert response.status_code in range(300, 400), "Did not get a redirect"
