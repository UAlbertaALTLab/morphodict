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
def test_analyze_wordform(wordform, lemma, suffix):
    analysis, *_more_analyses = analyze(wordform)
    assert analysis.lemma == lemma
    assert suffix in analysis.raw_suffixes


@pytest.mark.parametrize(
    "wordform,lemma,prefix",
    [
        ("ê-kî-kotiskâwêyâhk", "kotiskâwêw", "PV/e"),
        ("ê-kî-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "PV/kimoci"),
        ("ê-kî-kâh-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "PV/kah"),
        ("ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "PV/nitawi"),
    ],
)
def test_analyze_with_prefix(wordform, lemma, prefix):
    analysis, *_more_analyses = analyze(wordform)
    assert analysis.lemma == lemma
    assert prefix in analysis.raw_prefixes
    assert "AI" in analysis.raw_suffixes
    assert "Prt" in analysis.raw_suffixes
