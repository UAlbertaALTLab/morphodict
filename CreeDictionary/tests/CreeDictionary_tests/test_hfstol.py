#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest

from CreeDictionary.hfstol import analyze


@pytest.mark.parametrize(
    "wordform,lemma,suffix",
    [
        ("wâpamêw", "wâpamêw", "TA"),
        ("niskak", "niska", "A"),
        ("maskwak", "maskwa", "Pl"),
        ("maskos", "maskwa", "Der/Dim"),
        ("nimaskom", "maskwa", "Px1Sg"),
    ],
)
def test_analzye_wordform(wordform, lemma, suffix):
    analysis, *_more_analyses = analyze(wordform)
    assert analysis.lemma == lemma
    assert suffix in analysis.raw_suffixes
