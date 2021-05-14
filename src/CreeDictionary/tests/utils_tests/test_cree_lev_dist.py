from string import ascii_letters

import pytest
from hypothesis import assume, example, given
from hypothesis.strategies import text
from Levenshtein import distance
from CreeDictionary.utils import get_modified_distance


@given(text(alphabet=ascii_letters), text(alphabet=ascii_letters))
@example("", "")
@example("some_word", "")
def test_get_distance_basic_lev(spelling: str, normal_form: str):
    """
    make sure the modified distance gets basic lev distance right
    """
    assume("h" not in spelling.lower() and "h" not in normal_form.lower())

    assert get_modified_distance(spelling, normal_form) == distance(
        spelling.lower(), normal_form.lower()
    )


@pytest.mark.parametrize(
    ("spelling", "normal_form", "expected_distance"),
    (
        ["atâk", "atâhk", 0.5],  # an 'h' in a rime is not added
        ["ah", "a", 0.5],  # an extra 'h' in a rime is added
        ["atahk", "atâhk", 0.5],  # a circumflex is not added
        ["wâpamew", "wâpamêw", 0],  # a circumflex on 'e' is omitted, don't punish
        ["atak", "atâhk", 1],  # both circumflex and h in a rime is not added
        [
            "adak",
            "atâhk",
            2,
        ],  # both circumflex and h in a rime is not added and spelling error t -> d
    ),
)
def test_get_distance(spelling: str, normal_form: str, expected_distance):
    assert get_modified_distance(spelling, normal_form) == expected_distance
