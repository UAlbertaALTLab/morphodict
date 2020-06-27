#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Test the integration of itwêwina's settings.py against the morphodict application.
"""

import pytest

from morphodict.orthography import ORTHOGRAPHY


def test_morphodict_orthography():
    assert ORTHOGRAPHY.default == "Latn"
    assert {"Latn", "Cans", "Latn-x-macron"} <= set(ORTHOGRAPHY.available)


@pytest.mark.parametrize(
    "code,name,example",
    [
        ("Latn", "SRO", "amiskwaciy-wâskahikanihk"),
        ("Latn-x-macron", "SRO", "amiskwaciy-wāskahikanihk"),
        ("Cans", "Syllabics", "ᐊᒥᐢᑿᒋᐩ ᐚᐢᑲᐦᐃᑲᓂᕽ"),
    ],
)
def test_each_orthography(code, name, example):
    internal_text = "amiskwaciy-wâskahikanihk"
    assert name in ORTHOGRAPHY.name_of(code)
    assert callable(ORTHOGRAPHY.converter[code])
    assert ORTHOGRAPHY.converter[code](internal_text) == example
