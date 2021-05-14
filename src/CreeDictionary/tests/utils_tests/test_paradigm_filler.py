"""
Tests importing the NA layouts.

Note: if the upstream layouts change, so will these tests!
"""
from string import Template

import pytest
from CreeDictionary.utils import ParadigmSize, WordClass

from CreeDictionary.CreeDictionary.paradigm.filler import (
    EmptyRow,
    Heading,
    InflectionCell,
    Label,
    ParadigmFiller,
    import_layouts,
)


def test_import_prefilled_layouts(shared_datadir) -> None:
    """
    Imports ALL of the layouts, and makes sure a NA gets filled out.
    """
    # these layout and paradigm files are pinned test data
    # the real files in use are hosted under res/ folder
    prefilled_layouts = ParadigmFiller._import_layouts(shared_datadir / "layouts")
    assert prefilled_layouts[WordClass.NA, ParadigmSize.BASIC] == [
        [Label("One"), InflectionCell(Template("${lemma}+N+A+Sg"))],
        [Label("Many"), InflectionCell(Template("${lemma}+N+A+Pl"))],
        [Label("Further"), InflectionCell(Template("${lemma}+N+A+Obv"))],
        EmptyRow,
        # TODO: This should be a title, not a heading
        ["", Heading("Smaller/Lesser/Younger")],
        [Label("One"), InflectionCell(Template("${lemma}+N+A+Der/Dim+N+A+Sg"))],
        EmptyRow,
        # TODO: This should be a title row, not a label ¯\_(ツ)_/¯
        ["", Heading("Ownership")],
        ["", Heading("One")],
        [Label("my"), InflectionCell(Template("${lemma}+N+A+Px1Sg+Sg"))],
        [
            Label("your (one)"),
            InflectionCell(Template("${lemma}+N+A+Px2Sg+Sg")),
        ],
        ["", Heading("Further")],
        [Label("his/her"), InflectionCell(Template("${lemma}+N+A+Px3Sg+Obv"))],
    ]


@pytest.mark.parametrize(
    "lemma,wordclass,examples",
    [
        ("wâpamêw", WordClass.VTA, {"kiwâpamitin", "kiwâpamin", "ê-wâpamit", "wâpam"}),
        ("mîcisow", WordClass.VAI, {"nimîcison", "kimîcison", "ê-mîcisot"}),
        ("wâpahtam", WordClass.VTI, {"niwâpahtên", "kiwâpahtên", "ê-wâpahtahk"}),
        ("nîpin", WordClass.VII, {"ê-nîpihk"}),
        ("nôhkom", WordClass.NAD, {"kôhkom", "ohkoma", "nôhkomak"}),
        ("mîpit", WordClass.NID, {"nîpit", "kîpit", "wîpit"}),
        ("maskwa", WordClass.NA, {"maskwak", "maskos"}),
        ("nipiy", WordClass.NI, {"nipiya", "nipîhk"}),
    ],
)
def test_inflect_all(
    paradigm_filler, lemma: str, wordclass: WordClass, examples: set
) -> None:
    forms = paradigm_filler.inflect_all(lemma, wordclass)
    assert lemma in forms
    assert examples <= forms


def test_inflect_all_with_analyses(paradigm_filler) -> None:
    """
    Smoke test for inflect_all_with_analyses()
    """

    lemma = "wâpamêw"
    stem = "wâpam"
    inflections = paradigm_filler.inflect_all_with_analyses(lemma, WordClass.VTA)

    assert len(inflections.keys()) >= 1

    analysis = next(iter(inflections.keys()))
    assert lemma in analysis
    assert "+" in analysis, "expected to find the tag separator in the analysis"

    all_forms = [form for inflection in inflections.values() for form in inflection]
    assert len(all_forms) >= len(inflections)
    random_form = all_forms[0]
    assert (
        stem in random_form
    ), f"could not find stem {stem} in regular inflection {random_form}"


@pytest.fixture
def paradigm_filler(shared_datadir) -> ParadigmFiller:
    """
    These layout, paradigm, and hfstol files are **pinned** test data;
    the real files in use are hosted under res/ folder, and should not
    be used in tests!
    """
    return ParadigmFiller(
        shared_datadir / "layouts",
        shared_datadir / "crk-normative-generator.hfstol",
    )


def test_import_layouts_na_basic(shared_datadir) -> None:
    """
    Ensure that we can import paradigm layout templates from the plain text files.
    """

    imported_layout = import_layouts(shared_datadir / "layouts")
    assert imported_layout[WordClass.NA, ParadigmSize.BASIC] == [
        ['"One"', "${lemma}+N+A+Sg"],
        ['"Many"', "${lemma}+N+A+Pl"],
        ['"Further"', "${lemma}+N+A+Obv"],
        [""],
        ["", ': "Smaller/Lesser/Younger"'],
        ['"One"', "${lemma}+N+A+Der/Dim+N+A+Sg"],
        [""],
        ["", ': "Ownership"'],
        ["", ': "One"'],
        ['"my"', "${lemma}+N+A+Px1Sg+Sg"],
        ['"your (one)"', "${lemma}+N+A+Px2Sg+Sg"],
        ["", ': "Further"'],
        ['"his/her"', "${lemma}+N+A+Px3Sg+Obv"],
    ]
