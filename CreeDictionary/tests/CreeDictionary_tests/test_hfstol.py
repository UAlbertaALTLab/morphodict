#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest

from CreeDictionary.hfstol import analyze, generate


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
        ("nêpat", "nipâw", "IC"),
    ],
)
def test_analyze_with_prefix(wordform, lemma, prefix):
    analysis, *_more_analyses = analyze(wordform)
    assert analysis.lemma == lemma
    assert prefix in analysis.raw_prefixes
    assert "AI" in analysis.raw_suffixes
    assert "Cnj" in analysis.raw_suffixes


def test_analyze_nonword():
    # "pîpîpôpô" is not a real word
    assert list(analyze("pîpîpôpô")) == []


@pytest.mark.parametrize(
    "analysis,wordform",
    [
        ("wâpamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO", "wâpamêw"),
        ("PV/e+wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO", "ê-wâpamât"),
        ("IC+nipâw+V+AI+Cnj+Prs+3Sg", "nêpât"),
    ],
)
def test_generate(analysis, wordform):
    """
    Simple test of generating wordforms.
    """
    assert wordform in list(generate(analysis))


def test_generate_non_word():
    assert [] == list(generate("pîpîpôpô+Ipc"))
