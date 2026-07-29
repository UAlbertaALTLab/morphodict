import pytest

from morphodict.phrase_translate.to_target import inflect_target_language_phrase

ARBITRARY_DEFINITION = "s/he sees s.o."


@pytest.mark.parametrize(
    ("analysis", "definition", "english_phrase"),
    (
        (
            (
                (),
                "target_lemma_for_book_(irrelevant_for_test)",
                ("+N", "+Dim", "+Px1Sg", "+Loc"),
            ),
            "book",
            "in my little book",
        ),
        (
            (
                (),
                "target_lemma_for_book_(irrelevant_for_test)",
                ("+N", "+I", "+Px12Pl", "+Pl"),
            ),
            "book",
            "your and our books",
        ),
        (
            (
                (),
                "target_lemma_for_star_(irrelevant_for_test)",
                ("+N", "+A", "+Der/Dim", "+N", "+A", "+Obv"),
            ),
            "star",
            "an/other little star(s)",
        ),
        (
            (
                (),
                "target_lemma_for_cree_book_(irrelevant_for_test)",
                ("+N", "+I", "+Der/Dim", "+N", "+I", "+Px1Sg", "+Loc"),
            ),
            "Cree book",
            "in my little Cree book",
        ),
        (
            (
                ("PV/e+",),
                "target_lemma_for_long_definition_(irrelevant_for_test)",
                ("+V", "+TA", "+Cnj", "+1Sg", "+2SgO"),
            ),
            "s/he sits with s.o., s/he stays with s.o., s/he is present with s.o.",
            "as I sit with you, as I stay with you, as I am present with you",
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Fut", "+Cond", "+2Sg", "+3SgO"),
            ),
            ARBITRARY_DEFINITION,
            "when you see him/her",
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Imp", "+Imm", "+12Pl", "+3SgO"),
            ),
            ARBITRARY_DEFINITION,
            "let you and us see him/her now",
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Imp", "+Del", "+2Sg", "+3PlO"),
            ),
            ARBITRARY_DEFINITION,
            "(you) see them later",
        ),
        (
            (
                ("PV/ki+",),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Ind", "+2Pl", "+1PlO"),
            ),
            ARBITRARY_DEFINITION,
            "you all saw us",
        ),
        (
            (
                ("PV/wi+",),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Ind", "+4Sg/Pl", "+3PlO"),
            ),
            ARBITRARY_DEFINITION,
            "another/others are going to see them",
        ),
        (
            (
                ("PV/e+", "PV/wi+"),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Cnj", "+1Sg", "+3PlO"),
            ),
            ARBITRARY_DEFINITION,
            "as I am going to see them",
        ),
        (
            (
                ("PV/ka+",),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Ind", "+4Sg/Pl", "+3SgO"),
            ),
            ARBITRARY_DEFINITION,
            "another/others will see him/her",
        ),
        (
            (
                ("PV/ka+",),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+TA", "+Cnj", "+1Sg", "+2PlO"),
            ),
            ARBITRARY_DEFINITION,
            "for me to see you all",
        ),
    ),
)
def test_translations(analysis, definition, english_phrase):
    assert inflect_target_language_phrase(analysis, definition) == english_phrase


TSUUTINA_ARBITRARY_DEFINITION = "he/she/it will ask him/her/it"


@pytest.mark.parametrize(
    ("analysis", "definition", "english_phrase", "extra_args"),
    (
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Ipfv", "+SbjSg1", "+DObjSg3"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "I will ask him/her/it",
            {},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Prog", "+SbjSg1", "+DObjSg3"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "I am asking him/her/it",
            {"adjust_tense": "event"},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Pfv", "+SbjPl2", "+DObjSg3"),
            ),  # V+T+Pfv as well"
            TSUUTINA_ARBITRARY_DEFINITION,
            "you both asked him/her/it",
            {"adjust_tense": "event"},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Prog", "+SbjPl2", "+DObjSg3", "+Distr"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "each and every one of you is asking him/her/it",
            {"adjust_tense": "event"},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Ipfv", "+Rep", "+SbjSg2", "+DObjSg3"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "you ask him/her/it again and again",
            {"adjust_tense": "event"},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Pot", "+SbjSg3", "+DObjSg3", "+Nomz"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "the one who might ask him/her/it",
            {"adjust_tense": "event"},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Pot", "+SbjPl3", "+DObjSg3", "+Distr"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "each and every one of them might ask him/her/it",
            {"adjust_tense": "event"},
        ),
        (
            (
                (),
                "target_arbitrary_lemma_(irrelevant_for_test)",
                ("+V", "+T", "+Pfv", "+SbjPl3", "+DObjSg3", "+Distr"),
            ),
            TSUUTINA_ARBITRARY_DEFINITION,
            "each and every one of them asked him/her/it",
            {"adjust_tense": "event"},
        ),
    ),
)
def test_tsuutina_translations(analysis, definition, english_phrase, extra_args):
    inflection = inflect_target_language_phrase(analysis, definition, False, extra_args)
    assert inflection == english_phrase
