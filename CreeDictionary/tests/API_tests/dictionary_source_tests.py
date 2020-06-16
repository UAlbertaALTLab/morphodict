#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Tests things related to the dictionary sources.
"""

import pytest

from API.models import Definition, DictionarySource, Wordform


@pytest.mark.django_db
def test_create_dictionary_source():
    """
    Sanity check: make sure we can create a DictionarySource instance and save
    it.
    """

    source = DictionarySource(abbrv="CW", title="Cree: Words", editor="Arok Wolvengrey")
    source.save()

    assert source.pk == "CW"


@pytest.mark.django_db
def test_link_definition_to_dictionary():
    """
    Ensure a definition can exist with a dictionary source.
    """

    # Create a lemma and a definition for it.
    acâhkos = Wordform(id=0, text="acâhkos", lemma_id=0)
    acâhkos.save()

    dfn = Definition(id=0, text="little star", lemma=acâhkos)
    dfn.save()

    cw = DictionarySource("CW")
    cw.save()

    dfn.citations.add(cw)

    assert dfn.source_ids == ("CW",)
