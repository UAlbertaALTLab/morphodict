#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests things related to the dictionary sources.
"""

import pytest

from API.models import Definition, DictionarySource


@pytest.mark.django_db
def test_create_dictionary_source():
    """
    Sanity test: make sure we can create a DictionarySource instance and save
    it.
    """

    source = DictionarySource(abbrv="CW", title="Cree: Words", editor="Arok Wolvengrey")
    source.save()

    assert source.pk == "CW"
