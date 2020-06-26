#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from morphodict.orthography import ORTHOGRAPHY


def test_morphodict_orthography():
    assert ORTHOGRAPHY.default == "Latn"
    assert {"Latn", "Cans", "Latn-x-macron"} <= set(ORTHOGRAPHY.available)
    assert "SRO" in ORTHOGRAPHY.name_of("Latn")
    assert "SRO" in ORTHOGRAPHY.name_of("Latn-x-macron")
    assert "Syllabics" in ORTHOGRAPHY.name_of("Cans")
