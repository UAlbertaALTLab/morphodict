import pytest

from CreeDictionary.CreeDictionary.hfstol import analyze, generate


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
        ("ê-kî-kâh-kîmôci-kotiskâwêyâhk", "kotiskâwêw", "RdplS"),
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
        ("wâpamêw+V+TA+Ind+3Sg+4Sg/PlO", "wâpamêw"),
        ("PV/e+wâpamêw+V+TA+Cnj+3Sg+4Sg/PlO", "ê-wâpamât"),
        ("IC+nipâw+V+AI+Cnj+3Sg", "nêpât"),
    ],
)
def test_generate(analysis, wordform):
    """
    Simple test of generating wordforms.
    """
    assert wordform in list(generate(analysis))


def test_generate_non_word():
    assert [] == list(generate("pîpîpôpô+Ipc"))


def test_analyses_do_not_contain_err_orth():
    """
    Regression: old FSTs used to contain an +Err/Orth tag that made invalidated some
    assumptions in the rest of the codebase.
    """
    # old FSTs produce +Err/Orth if when the hyphen is missing between ê- and *wâpamât
    non_standard_form = "êwâpamât"
    assert all(
        "+Err/Orth" not in analysis.raw_suffixes
        for analysis in analyze(non_standard_form)
    )


def test_analyses_do_not_contain_err_frag():
    """
    Regression: old FSTs used to produce MANY analyses, incling ones called +Err/Frag
    that are only useful in tagging documents — but confuse dictionary applications!
    """
    possible_fragment = "kâ"
    assert all(
        "+Err/Frag" not in analysis.raw_suffixes
        for analysis in analyze(possible_fragment)
    )
