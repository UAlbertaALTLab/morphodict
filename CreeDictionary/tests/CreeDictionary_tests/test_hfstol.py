#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest

from CreeDictionary.hfstol import analyze


@pytest.mark.parametrize(
    "wordform,lemma",
    [
        ("wâpamêw", "wâpamêw"),
        ("niskak", "niska"),
        ("maskwak", "maskwa"),
        ("maskos", "maskwa"),
        ("nimaskom", "maskwa"),
    ],
)
def test_analzye_wordform(wordform, lemma):
    analysis, *_more_analyses = analyze(wordform)
    assert analysis.lemma == lemma
