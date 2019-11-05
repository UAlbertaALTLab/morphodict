import pytest

from constants import LC, ParadigmSize
from paradigm import Heading, Label
from shared import paradigm_filler
from utils import shared_res_dir
from utils.paradigm_filler import import_prefilled_layouts


def test_import_prefilled_layouts() -> None:
    """
    Imports ALL of the layouts, and makes sure a NA gets filled out.

    Note: if the upstream layouts change, so will this test!
    """
    prefilled_layouts = import_prefilled_layouts(shared_res_dir / "prefilled_layouts")
    assert prefilled_layouts[LC.NA, ParadigmSize.BASIC] == [
        [Label("One"), "{{ lemma }}+N+A+Sg"],
        [Label("Many"), "{{ lemma }}+N+A+Pl"],
        [Label("Further"), "{{ lemma }}+N+A+Obv"],
        ["", ""],
        ["", Heading("Smaller/Lesser/Younger")],
        [Label("One"), "{{ lemma }}+N+A+Der/Dim+N+A+Sg"],
        ["", ""],
        ["", Heading("Ownership")],
        ["", Heading("One")],
        [Label("my"), "{{ lemma }}+N+A+Px1Sg+Sg"],
        [Label("your (one)"), "{{ lemma }}+N+A+Px2Sg+Sg"],
        ["", Heading("Further")],
        [Label("his/her"), "{{ lemma }}+N+A+Px3Sg+Obv"],
    ]


@pytest.mark.parametrize(
    "lemma,  inflection_category, paradigm_size, expected_table",
    [
        (
            "niska",
            LC.NA,
            ParadigmSize.FULL,
            [
                [
                    [Label("One"), "niska", "", "", ""],
                    [Label("Many"), "niskak", "", "", ""],
                    [Label("Further"), "niska", "", "", ""],
                    [Label("In/On"), "niskihk", "", "", ""],
                    [Label("Among"), "niskinâhk", "", "", ""],
                ],
                [
                    ["", Label("Smaller/Lesser/Younger"), "", "", ""],
                    [Label("One"), "niskis / niskisis", "", "", ""],
                    [Label("Many"), "niskisak / niskisisak", "", "", ""],
                    [Label("Further"), "niskisa / niskisisa", "", "", ""],
                    [Label("In/On"), "niskisihk / niskisisihk", "", "", ""],
                    [Label("Among"), "niskisinâhk / niskisisinâhk", "", "", ""],
                ],
                [
                    ["", Label("Ownership"), "", "", ""],
                    [
                        "",
                        Heading("One"),
                        Heading("Many"),
                        Heading("Further"),
                        Heading("In/On"),
                    ],
                    [Label("my"), "niniskim", "niniskimak", "niniskima", "niniskimihk"],
                    [
                        Label("your (one)"),
                        "kiniskim",
                        "kiniskimak",
                        "kiniskima",
                        "kiniskimihk",
                    ],
                    [Label("his/her"), "", "", "oniskima", "oniskimihk"],
                    [
                        Label("our"),
                        "niniskiminân",
                        "niniskiminânak",
                        "niniskiminâna",
                        "niniskiminâhk",
                    ],
                    [
                        Label("your and our"),
                        "kiniskiminaw",
                        "kiniskiminawak",
                        "kiniskiminawa",
                        "kiniskiminâhk",
                    ],
                    [
                        Label("your (all)"),
                        "kiniskimiwâw",
                        "kiniskimiwâwak",
                        "kiniskimiwâwa",
                        "kiniskimiwâhk",
                    ],
                    [Label("their"), "", "", "oniskimiwâwa", "oniskimiwâhk"],
                    [
                        Label("his/her/their (further)"),
                        "",
                        "",
                        "oniskimiyiwa",
                        "oniskimiyihk",
                    ],
                ],
                [
                    ["", Label("Smaller/Lesser/Younger"), "", "", ""],
                    ["", Label("Ownership"), "", "", ""],
                    [
                        "",
                        Heading("One"),
                        Heading("Many"),
                        Heading("Further"),
                        Heading("In/On"),
                    ],
                    [
                        Label("my"),
                        "niniskimis / niniskimisis",
                        "niniskimisak / niniskimisisak",
                        "niniskimisa / niniskimisisa",
                        "niniskimisihk / niniskimisisihk",
                    ],
                    [
                        Label("your (one)"),
                        "kiniskimis / kiniskimisis",
                        "kiniskimisak / kiniskimisisak",
                        "kiniskimisa / kiniskimisisa",
                        "kiniskimisihk / kiniskimisisihk",
                    ],
                    [
                        Label("his/her"),
                        "",
                        "",
                        "oniskimisa / oniskimisisa",
                        "oniskimisihk / oniskimisisihk",
                    ],
                    [
                        Label("our"),
                        "niniskimisinân / niniskimisisinân",
                        "niniskimisinânak / niniskimisisinânak",
                        "niniskimisinâna / niniskimisisinâna",
                        "niniskimisinâhk / niniskimisisinâhk",
                    ],
                    [
                        Label("your and our"),
                        "kiniskimisinaw / kiniskimisisinaw",
                        "kiniskimisinawak / kiniskimisisinawak",
                        "kiniskimisinawa / kiniskimisisinawa",
                        "kiniskimisinâhk / kiniskimisisinâhk",
                    ],
                    [
                        Label("your (all)"),
                        "kiniskimisisiwâw / kiniskimisiwâw",
                        "kiniskimisisiwâwak / kiniskimisiwâwak",
                        "kiniskimisisiwâwa / kiniskimisiwâwa",
                        "kiniskimisisiwâhk / kiniskimisiwâhk",
                    ],
                    [
                        Label("their"),
                        "",
                        "",
                        "oniskimisisiwâwa / oniskimisiwâwa",
                        "oniskimisisiwâhk / oniskimisiwâhk",
                    ],
                    [
                        Label("his/her/their (further)"),
                        "",
                        "",
                        "oniskimisisiyiwa / oniskimisiyiwa",
                        "oniskimisisiyihk / oniskimisiyihk",
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
