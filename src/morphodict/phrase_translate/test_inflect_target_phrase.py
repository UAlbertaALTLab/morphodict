import pytest

from morphodict.phrase_translate.fst import inflect_english_phrase

ARBITRARY_DEFINITION = "s/he sees s.o."


@pytest.mark.parametrize(
    ("analysis", "definition", "english_phrase"),
    (
        (
            ((), "target_lemma_for_book_(irrelevant_for_test)", ("+N", "+Dim", "+Px1Sg", "+Loc")),
            "book",
            "in my little book",
        ),
        (
            ((), "target_lemma_for_book_(irrelevant_for_test)", ("+N", "+I", "+Px12Pl", "+Pl")),
            "book",
            "your and our books",
        ),
        (
            ((), "target_lemma_for_star_(irrelevant_for_test)", ("+N", "+A", "+Der/Dim", "+N", "+A", "+Obv")),
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
            (("PV/e+",), "target_lemma_for_long_definition_(irrelevant_for_test)", ("+V", "+TA", "+Cnj", "+1Sg", "+2SgO")),
            "s/he sits with s.o., s/he stays with s.o., s/he is present with s.o.",
            "I sit with you, I stay with you, I am present with you",
        ),
        (
            ((), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Fut", "+Cond", "+2Sg", "+3SgO")),
            ARBITRARY_DEFINITION,
            "when you see him/her",
        ),
        (
            ((), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Imp", "+Imm", "+12Pl", "+3SgO")),
            ARBITRARY_DEFINITION,
            "let you and us see him/her now",
        ),
        (
            ((), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Imp", "+Del", "+2Sg", "+3PlO")),
            ARBITRARY_DEFINITION,
            "(you) see them later",
        ),
        (
            (("PV/ki+",), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Ind", "+2Pl", "+1PlO")),
            ARBITRARY_DEFINITION,
            "you all saw us",
        ),
        (
            (("PV/wi+",), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Ind", "+4Sg/Pl", "+3PlO")),
            ARBITRARY_DEFINITION,
            "another/others are going to see them",
        ),
        (
            (("PV/e+", "PV/wi+"), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Cnj", "+1Sg", "+3PlO")),
            ARBITRARY_DEFINITION,
            "I am going to see them",
        ),
        (
            (("PV/ka+",), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Ind", "+4Sg/Pl", "+3SgO")),
            ARBITRARY_DEFINITION,
            "another/others will see him/her",
        ),
        (
            (("PV/ka+",), "target_arbitrary_lemma_(irrelevant_for_test)", ("+V", "+TA", "+Cnj", "+1Sg", "+2PlO")),
            ARBITRARY_DEFINITION,
            "for me to see you all",
        ),
    ),
)
def test_translations(analysis, definition, english_phrase):
    assert inflect_english_phrase(analysis, definition) == english_phrase
