import pytest

from CreeDictionary.phrase_translate.definition_processing import remove_parentheticals

SHOULD_NOT_CHANGE = object()


@pytest.mark.parametrize(
    "input, expected",
    [
        ("S/he sees it", SHOULD_NOT_CHANGE),
        (
            "He darkens quickly. Animate. E.g. the power went out.",
            "He darkens quickly.",
        ),
        ("Those things. Inanimate.", "Those things."),
        ("Earth. Also land.", "Earth."),
        ("He knits. Or he braids.", "He knits."),
        ("helmet (of metal)", "helmet"),
        ("timber wolf; [canis lupus]", "timber wolf"),
        ("s/he opens (it/him) for s.o.", SHOULD_NOT_CHANGE),
        ("s/he embroiders (it) for people", SHOULD_NOT_CHANGE),
        ("s/he has (s.o. as) a mother", SHOULD_NOT_CHANGE),
        ("s/he has (s.t. as) a supply of food", SHOULD_NOT_CHANGE),
        ("s/he runs to fetch (s.t.)", SHOULD_NOT_CHANGE),
        ("He (it) turns or goes around. Animate.", "He (it) turns or goes around."),
    ],
)
def test_remove_parentheticals(input, expected):
    if expected == SHOULD_NOT_CHANGE:
        expected = input
    assert remove_parentheticals(input) == expected
