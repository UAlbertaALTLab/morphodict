#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Integration test of settings.py and morphodict application.
"""

import pytest

from morphodict.orthography import ORTHOGRAPHY


def test_morphodict_orthography():
    assert ORTHOGRAPHY.default == "Latn"
    assert {"Latn", "Cans", "Latn-x-macron"} <= set(ORTHOGRAPHY.available)


@pytest.mark.parametrize(
    "code,name", [("Latn", "SRO"), ("Latn-x-macron", "SRO"), ("Cans", "Syllabics"),]
)
def test_each_orthography(code, name):
    assert name in ORTHOGRAPHY.name_of(code)
    assert callable(ORTHOGRAPHY.converter[code])
