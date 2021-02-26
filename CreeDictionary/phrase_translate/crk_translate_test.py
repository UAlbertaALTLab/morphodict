import pytest

from phrase_translate.translate import inflect_english_phrase

WAPAMEW_DEFINITION = "s/he sees s.o."


@pytest.mark.parametrize(
    ("analysis", "definition", "english_phrase"),
    (
        ("masinahikan+N+Dim+Px1Sg+Loc", "book", "in my little book"),
        ("atâhk+N+A+Der/Dim+N+A+Obv", "star", "little star over there"),
        (
            "nêhiyawasinahikan+N+I+Der/Dim+N+I+Px1Sg+Loc",
            "Cree book",
            "in my little Cree book",
        ),
        (
            "PV/e+wîtatoskêmêw+V+TA+Cnj+1Sg+2SgO",
            "s/he works together with s.o.",
            "I work together with you",
        ),
        (
            "PV/e+wîtapimêw+V+TA+Cnj+1Sg+2SgO",
            "s/he sits with s.o., s/he stays with s.o., s/he is present with s.o.",
            "I sit with you, I stay with you, I am present with you",
        ),
        ("wâpamêw+V+TA+Fut+Cond+2Sg+3SgO", WAPAMEW_DEFINITION, "when you see him/her"),
        (
            "wâpamêw+V+TA+Imp+Imm+12Pl+3SgO",
            WAPAMEW_DEFINITION,
            "let you and us see him/her now",
        ),
        ("wâpamêw+V+TA+Imp+Del+2Sg+3PlO", WAPAMEW_DEFINITION, "let you see them later"),
        (
            "PV/ki+wâpamêw+V+TA+Ind+2Pl+1PlO",
            WAPAMEW_DEFINITION,
            "you all see>ed us",
        ),
        (
            "PV/wi+wâpamêw+V+TA+Ind+4Sg/Pl+3PlO",
            WAPAMEW_DEFINITION,
            "s/he/they want to see them",
        ),
        (
            "PV/e+PV/wi+wâpamêw+V+TA+Cnj+1Sg+3PlO",
            WAPAMEW_DEFINITION,
            "I want to see them",
        ),
    ),
)
def test_translations(analysis, definition, english_phrase):
    assert inflect_english_phrase(analysis, definition) == english_phrase
