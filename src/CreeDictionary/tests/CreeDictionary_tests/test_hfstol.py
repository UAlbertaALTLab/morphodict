import pytest

from morphodict.analysis import (
    relaxed_analyzer,
    rich_analyze_relaxed,
    strict_generator,
)


@pytest.mark.parametrize(
    "wordform,lemma,suffix",
    [
        ("wâpamêw", "wâpamêw", "+TA"),
        ("niskak", "niska", "+A"),
        ("maskwak", "maskwa", "+Pl"),
        ("maskos", "maskwa", "+Der/Dim"),
        ("nimaskom", "maskwa", "+Px1Sg"),
    ],
)
def test_analyze_wordform(wordform, lemma, suffix):
    assert any(
        analysis.lemma == lemma and suffix in analysis.suffix_tags
        for analysis in rich_analyze_relaxed(wordform)
    )


@pytest.mark.parametrize(
    "wordform,lemma,prefix",
    [
        ("ê-kî-kotiskâwêyâhk", "kotiskâwêw", "PV/e+"),
        ("ê-kî-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "PV/kimoci+"),
        ("ê-kî-kâh-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "RdplS+"),
        ("ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "PV/nitawi+"),
        ("nêpat", "nipâw", "IC+"),
    ],
)
def test_analyze_with_prefix(wordform, lemma, prefix):
    analysis, *_more_analyses = rich_analyze_relaxed(wordform)
    assert analysis.lemma == lemma
    assert prefix in analysis.prefix_tags
    assert "+AI" in analysis.suffix_tags
    assert "+Cnj" in analysis.suffix_tags


def test_analyze_nonword():
    # "pîpîpôpô" is not a real word
    assert list(relaxed_analyzer().lookup("pîpîpôpô")) == []


@pytest.mark.parametrize(
    "analysis,wordform",
    [
        ("wâpamêw+V+TA+Ind+3Sg+4Sg/PlO", "wâpamêw"),
        ("PV/e+wâpamêw+V+TA+Cnj+3Sg+4Sg/PlO", "ê-wâpamât"),
        ("IC+nipâw+V+AI+Cnj+3Sg", "nêpât"),
    ],
)
def test_generate(analysis, wordform):
    """
    Simple test of generating wordforms.
    """
    assert wordform in list(strict_generator().lookup(analysis))


def test_generate_non_word():
    assert [] == list(strict_generator().lookup("pîpîpôpô+Ipc"))


def test_analyses_do_not_contain_err_orth():
    """
    Regression: old FSTs used to contain an +Err/Orth tag that made invalidated some
    assumptions in the rest of the codebase.
    """
    # old FSTs produce +Err/Orth if when the hyphen is missing between ê- and *wâpamât
    non_standard_form = "êwâpamât"
    assert all(
        "+Err/Orth" not in analysis.suffix_tags
        for analysis in rich_analyze_relaxed(non_standard_form)
    )


def test_analyses_do_not_contain_err_frag():
    """
    Regression: old FSTs used to produce MANY analyses, incling ones called +Err/Frag
    that are only useful in tagging documents — but confuse dictionary applications!
    """
    possible_fragment = "kâ"
    assert all(
        "+Err/Frag" not in analysis.suffix_tags
        for analysis in rich_analyze_relaxed(possible_fragment)
    )
