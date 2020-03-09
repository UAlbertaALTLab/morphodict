import pytest
from constants import ParadigmSize, SimpleLC
from paradigm import EmptyRow, Heading, Label, TitleRow
from shared import paradigm_filler
from utils import shared_res_dir
from utils.paradigm_filler import import_prefilled_layouts


def test_import_prefilled_layouts() -> None:
    """
    Imports ALL of the layouts, and makes sure a NA gets filled out.

    Note: if the upstream layouts change, so will this test!
    """
    prefilled_layouts = import_prefilled_layouts(shared_res_dir / "prefilled_layouts")
    assert prefilled_layouts[SimpleLC.NA, ParadigmSize.BASIC] == [
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
            SimpleLC.NA,
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
                    [Label(text="Many"), "niskisak", "", "", ""],
                    [Label(text="Further"), "niskisa", "", "", ""],
                    [Label(text="In/On"), "niskisihk", "", "", ""],
                    [Label(text="Among"), "niskisinâhk", "", "", ""],
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
                        Label(text="our"),
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
                [
                    TitleRow(title="Smaller/Lesser/Younger", span=5),
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
                        "niniskimis",
                        "niniskimisak",
                        "niniskimisa",
                        "niniskimisihk",
                    ],
                    [
                        Label(text="your (one)"),
                        "kiniskimis",
                        "kiniskimisak",
                        "kiniskimisa",
                        "kiniskimisihk",
                    ],
                    [Label(text="his/her"), "", "", "oniskimisa", "oniskimisihk"],
                    [
                        Label(text="our"),
                        "niniskimisinân",
                        "niniskimisinânak",
                        "niniskimisinâna",
                        "niniskimisinâhk",
                    ],
                    [
                        Label(text="your and our"),
                        "kiniskimisinaw",
                        "kiniskimisinawak",
                        "kiniskimisinawa",
                        "kiniskimisinâhk",
                    ],
                    [
                        Label(text="your (all)"),
                        "kiniskimisiwâw",
                        "kiniskimisiwâwak",
                        "kiniskimisiwâwa",
                        "kiniskimisiwâhk",
                    ],
                    [Label(text="their"), "", "", "oniskimisiwâwa", "oniskimisiwâhk"],
                    [
                        Label(text="his/her/their (further)"),
                        "",
                        "",
                        "oniskimisiyiwa",
                        "oniskimisiyihk",
                    ],
                ],
            ],
        )
    ],
)
def test_fill_NA_Full(lemma, inflection_category, paradigm_size, expected_table):
    assert (
        paradigm_filler.fill_paradigm(lemma, inflection_category, paradigm_size)
        == expected_table
    )
