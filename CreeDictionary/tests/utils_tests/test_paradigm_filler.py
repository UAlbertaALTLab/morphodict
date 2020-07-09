"""
Tests importing the NA layouts.

Note: if the upstream layouts change, so will these tests!
"""

import pytest
from paradigm import EmptyRow, Heading, Label, TitleRow
from utils import ParadigmSize, WordClass
from utils.paradigm_filler import ParadigmFiller


def test_import_prefilled_layouts(shared_datadir) -> None:
    """
    Imports ALL of the layouts, and makes sure a NA gets filled out.
    """
    # these layout and paradigm files are pinned test data
    # the real files in use are hosted under res/ folder
    prefilled_layouts = ParadigmFiller._import_layouts(
        shared_datadir / "layouts", shared_datadir / "paradigms"
    )
    assert prefilled_layouts[WordClass.NA, ParadigmSize.BASIC] == [
        [Label("One"), "{{ lemma }}+N+A+Sg"],
        [Label("Many"), "{{ lemma }}+N+A+Pl"],
        [Label("Further"), "{{ lemma }}+N+A+Obv"],
        EmptyRow,
        # TODO: I think there's a mistake with the source material here:
        # This should be a title row, not a label ¯\_(ツ)_/¯
        ["", Heading("Ownership")],
        ["", Heading("One")],
        [Label("my"), "{{ lemma }}+N+A+Px1Sg+Sg"],
        [Label("your (one)"), "{{ lemma }}+N+A+Px2Sg+Sg"],
        ["", Heading("Further")],
        [Label("his/her"), "{{ lemma }}+N+A+Px3Sg+Obv"],
        EmptyRow,
        # TODO: This should be a title, not a heading
        ["", Heading("Smaller/Lesser/Younger")],
        [Label("One"), "{{ lemma }}+N+A+Der/Dim+N+A+Sg"],
    ]


@pytest.mark.parametrize(
    "lemma,  inflection_category, paradigm_size, expected_table",
    [
        (
            "niska",
            WordClass.NA,
            ParadigmSize.FULL,
            [
                [
                    [Label(text="One"), "niska", "", "", ""],
                    [Label(text="Many"), "niskak", "", "", ""],
                    [Label(text="Further"), "niska", "", "", ""],
                    [Label(text="In/On"), "niskihk", "", "", ""],
                    [Label(text="Among"), "niskinâhk", "", "", ""],
                ],
                [
                    TitleRow(title="Smaller/Lesser/Younger", span=5),
                    [Label(text="One"), "niskis", "", "", ""],
                ],
                [
                    TitleRow(title="Ownership", span=5),
                    [
                        "",
                        Heading(text="One"),
                        Heading(text="Many"),
                        Heading(text="Further"),
                        Heading(text="In/On"),
                    ],
                    [
                        Label(text="my"),
                        "niniskim",
                        "niniskimak",
                        "niniskima",
                        "niniskimihk",
                    ],
                    [
                        Label(text="your (one)"),
                        "kiniskim",
                        "kiniskimak",
                        "kiniskima",
                        "kiniskimihk",
                    ],
                    [Label(text="his/her"), "", "", "oniskima", "oniskimihk"],
                    [
                        Label(text="our (but not your)"),
                        "niniskiminân",
                        "niniskiminânak",
                        "niniskiminâna",
                        "niniskiminâhk",
                    ],
                    [
                        Label(text="your and our"),
                        "kiniskiminaw",
                        "kiniskiminawak",
                        "kiniskiminawa",
                        "kiniskiminâhk",
                    ],
                    [
                        Label(text="your (all)"),
                        "kiniskimiwâw",
                        "kiniskimiwâwak",
                        "kiniskimiwâwa",
                        "kiniskimiwâhk",
                    ],
                    [Label(text="their"), "", "", "oniskimiwâwa", "oniskimiwâhk"],
                    [
                        Label(text="his/her/their (further)"),
                        "",
                        "",
                        "oniskimiyiwa",
                        "oniskimiyihk",
                    ],
                ],
            ],
        )
    ],
)
def test_fill_NA_Full(
    paradigm_filler, lemma, inflection_category, paradigm_size, expected_table
):
    assert (
        paradigm_filler.fill_paradigm(lemma, inflection_category, paradigm_size)
        == expected_table
    )


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


@pytest.fixture
def paradigm_filler(shared_datadir) -> ParadigmFiller:
    """
    hese layout, paradigm, and hfstol files are **pinned** test data;
    the real files in use are hosted under res/ folder, and should not
    be used in tests!
    """
    return ParadigmFiller(
        shared_datadir / "layouts",
        shared_datadir / "paradigms",
        shared_datadir / "crk-normative-generator.hfstol",
    )
