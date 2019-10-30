import pytest

from constants import LC, ParadigmSize
from shared import paradigm_filler
from utils import shared_res_dir
from utils.paradigm_filler import import_prefilled_layouts


def test_import_prefilled_layouts():
    prefilled_layouts = import_prefilled_layouts(shared_res_dir / "prefilled_layouts")
    assert prefilled_layouts[LC.NA, ParadigmSize.BASIC] == [
        ['"One"', "{{ lemma }}+N+A+Sg"],
        ['"Many"', "{{ lemma }}+N+A+Pl"],
        ['"Further"', "{{ lemma }}+N+A+Obv"],
        ["", ""],
        ["", ': "Smaller/Lesser/Younger"'],
        ['"One"', "{{ lemma }}+N+A+Der/Dim+N+A+Sg"],
        ["", ""],
        ["", ': "Ownership"'],
        ["", ': "One"'],
        ['"my"', "{{ lemma }}+N+A+Px1Sg+Sg"],
        ['"your (one)"', "{{ lemma }}+N+A+Px2Sg+Sg"],
        ["", ': "Further"'],
        ['"his/her"', "{{ lemma }}+N+A+Px3Sg+Obv"],
    ]


@pytest.mark.parametrize(
    "lemma,  inflection_category, paradigm_size, expected_table",
    [
        (
                "niska",
                LC.NA,
                ParadigmSize.FULL,
                [
                    ['"One"', "niska", "", "", ""],
                    ['"Many"', "niskak", "", "", ""],
                    ['"Further"', "niska", "", "", ""],
                    ['"In/On"', "niskihk", "", "", ""],
                    ['"Among"', "niskinâhk", "", "", ""],
                    ["", "", "", "", ""],
                    ["", '"Smaller/Lesser/Younger"', "", "", ""],
                    ['"One"', "niskis / niskisis", "", "", ""],
                    ['"Many"', "niskisak / niskisisak", "", "", ""],
                    ['"Further"', "niskisa / niskisisa", "", "", ""],
                    ['"In/On"', "niskisihk / niskisisihk", "", "", ""],
                    ['"Among"', "niskisinâhk / niskisisinâhk", "", "", ""],
                    ["", "", "", "", ""],
                    ["", '"Ownership"', "", "", ""],
                    ["", ': "One"', ': "Many"', ': "Further"', ': "In/On"'],
                    ['"my"', "niniskim", "niniskimak", "niniskima", "niniskimihk"],
                    ['"your (one)"', "kiniskim", "kiniskimak", "kiniskima", "kiniskimihk"],
                    ['"his/her"', "", "", "oniskima", "oniskimihk"],
                    [
                        '"our"',
                        "niniskiminân",
                        "niniskiminânak",
                        "niniskiminâna",
                        "niniskiminâhk",
                    ],
                    [
                        '"your and our"',
                        "kiniskiminaw",
                        "kiniskiminawak",
                        "kiniskiminawa",
                        "kiniskiminâhk",
                    ],
                    [
                        '"your (all)"',
                        "kiniskimiwâw",
                        "kiniskimiwâwak",
                        "kiniskimiwâwa",
                        "kiniskimiwâhk",
                    ],
                    ['"their"', "", "", "oniskimiwâwa", "oniskimiwâhk"],
                    ['"his/her/their (further)"', "", "", "oniskimiyiwa", "oniskimiyihk"],
                    ["", "", "", "", ""],
                    ["", '"Smaller/Lesser/Younger"', "", "", ""],
                    ["", '"Ownership"', "", "", ""],
                    ["", ': "One"', ': "Many"', ': "Further"', ': "In/On"'],
                    [
                        '"my"',
                        "niniskimis / niniskimisis",
                        "niniskimisak / niniskimisisak",
                        "niniskimisa / niniskimisisa",
                        "niniskimisihk / niniskimisisihk",
                    ],
                    [
                        '"your (one)"',
                        "kiniskimis / kiniskimisis",
                        "kiniskimisak / kiniskimisisak",
                        "kiniskimisa / kiniskimisisa",
                        "kiniskimisihk / kiniskimisisihk",
                    ],
                    [
                        '"his/her"',
                        "",
                        "",
                        "oniskimisa / oniskimisisa",
                        "oniskimisihk / oniskimisisihk",
                    ],
                    [
                        '"our"',
                        "niniskimisinân / niniskimisisinân",
                        "niniskimisinânak / niniskimisisinânak",
                        "niniskimisinâna / niniskimisisinâna",
                        "niniskimisinâhk / niniskimisisinâhk",
                    ],
                    [
                        '"your and our"',
                        "kiniskimisinaw / kiniskimisisinaw",
                        "kiniskimisinawak / kiniskimisisinawak",
                        "kiniskimisinawa / kiniskimisisinawa",
                        "kiniskimisinâhk / kiniskimisisinâhk",
                    ],
                    [
                        '"your (all)"',
                        "kiniskimisisiwâw / kiniskimisiwâw",
                        "kiniskimisisiwâwak / kiniskimisiwâwak",
                        "kiniskimisisiwâwa / kiniskimisiwâwa",
                        "kiniskimisisiwâhk / kiniskimisiwâhk",
                    ],
                    [
                        '"their"',
                        "",
                        "",
                        "oniskimisisiwâwa / oniskimisiwâwa",
                        "oniskimisisiwâhk / oniskimisiwâhk",
                    ],
                    [
                        '"his/her/their (further)"',
                        "",
                        "",
                        "oniskimisisiyiwa / oniskimisiyiwa",
                        "oniskimisisiyihk / oniskimisiyihk",
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
