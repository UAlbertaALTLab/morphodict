from string import ascii_letters

import pytest
from Levenshtein import distance
from Levenshtein import editops
from hypothesis import given, assume
from hypothesis.strategies import text

from utils import get_modified_distance
from utils.cree_lev_dist import EditOp


@given(text(alphabet=ascii_letters), text(alphabet=ascii_letters))
def test_apply_ops(s: str, t: str):
    ops = editops(s, t)
    assert EditOp.apply_ops(ops, s, t) == t


@given(text(alphabet=ascii_letters), text(alphabet=ascii_letters))
def test_get_distance_basic_lev(spelling: str, normal_form: str):
    """
    make sure the modified distance gets basic lev distance right
    """
    assume("h" not in spelling.lower() and "h" not in normal_form.lower())

    assert get_modified_distance(spelling, normal_form) == distance(
        spelling.lower(), normal_form.lower()
    )


# todo: use real world spelling examples here
@pytest.mark.parametrize(
    ("spelling", "normal_form", "expected_distance"),
    (
        ["atâk", "atâhk", 0.5],  # an 'h' in a rime is not added
        ["ah", "a", 0.5],  # an extra 'h' in a rime is added
        ["atahk", "atâhk", 0.5],  # a circumflex is not added
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
