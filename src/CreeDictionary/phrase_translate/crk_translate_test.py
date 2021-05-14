import pytest

from CreeDictionary.phrase_translate.translate import inflect_english_phrase

WAPAMEW_DEFINITION = "s/he sees s.o."


@pytest.mark.parametrize(
    ("analysis", "definition", "english_phrase"),
    (
        ("masinahikan+N+Dim+Px1Sg+Loc", "book", "in my little book"),
        ("masinahikan+N+I+Px12Pl+Pl", "book", "your and our books"),
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
        ("wâpamêw+V+TA+Imp+Del+2Sg+3PlO", WAPAMEW_DEFINITION, "(you) see them later"),
        (
            "PV/ki+wâpamêw+V+TA+Ind+2Pl+1PlO",
            WAPAMEW_DEFINITION,
            "you all saw us",
        ),
        (
            "PV/wi+wâpamêw+V+TA+Ind+4Sg/Pl+3PlO",
            WAPAMEW_DEFINITION,
            "s/he/they are going to see them",
        ),
        (
            "PV/e+PV/wi+wâpamêw+V+TA+Cnj+1Sg+3PlO",
            WAPAMEW_DEFINITION,
            "I am going to see them",
        ),
        (
            "PV/ka+wâpamêw+V+TA+Ind+4Sg/Pl+3SgO",
            WAPAMEW_DEFINITION,
            "s/he/they will see him/her",
        ),
        (
            "PV/ka+wâpamêw+V+TA+Cnj+1Sg+2PlO",
            WAPAMEW_DEFINITION,
            "for me to see you all",
        ),
        (
            "PV/ta+wâpamêw+V+TA+Cnj+3Sg+1PlO",
            WAPAMEW_DEFINITION,
            "for him/her to see us",
        ),
        (
            "wâpamêw+V+TA+Ind+4Sg/Pl+12PlO",
            WAPAMEW_DEFINITION,
            "s/he/they see you and us",
        ),
        (
            "atamihêw+V+TA+Ind+4Sg/Pl+2PlO",
            "s/he makes s.o. smile",
            "s/he/they make you all smile",
        ),
    ),
)
def test_translations(analysis, definition, english_phrase):
    assert inflect_english_phrase(analysis, definition) == english_phrase
