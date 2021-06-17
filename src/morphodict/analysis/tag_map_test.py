import re

import pytest

from morphodict.analysis.tag_map import TagMap, UnknownTagError


@pytest.fixture
def simple_tag_map():
    return TagMap(("+A", "abc+", 1))


def test_simple_tag_map(simple_tag_map):
    assert simple_tag_map.map_tags(["+A"]) == ["abc+"]


def test_raises_on_unknown_tag(simple_tag_map):
    with pytest.raises(UnknownTagError):
        simple_tag_map.map_tags(["+foo"])


@pytest.fixture
def tag_map_with_precedence():
    return TagMap(("+A", "abc+", 1), ("+B", TagMap.COPY_TAG_NAME, 2), ("+C", None, 0))


def test_map_with_precedence(tag_map_with_precedence):
    # No matter what order the input tags, the mapped tags should come out in
    # the order defined by precedence
    assert tag_map_with_precedence.map_tags(["+A", "+B"]) == ["abc+", "B+"]
    assert tag_map_with_precedence.map_tags(["+B", "+A"]) == ["abc+", "B+"]


def test_mapping_to_none(tag_map_with_precedence):
    assert tag_map_with_precedence.map_tags(["+C"]) == []


@pytest.fixture
def tag_map_with_multiples():
    return TagMap(
        ("+A", TagMap.COPY_TAG_NAME, 1),
        ("+A2", "A+", 1),
        ("+B", TagMap.COPY_TAG_NAME, 2),
    )


def test_dedupe(tag_map_with_multiples):
    assert tag_map_with_multiples.map_tags(["+A", "+A2"]) == ["A+"]
    assert tag_map_with_multiples.map_tags(["+A", "+B", "+A2"]) == ["A+", "B+"]


@pytest.fixture
def tag_map_wth_multi_map():
    return TagMap(
        (("+A", "+B"), "abc+", 1),
        ("+A", TagMap.COPY_TAG_NAME, 2),
        ("+B", TagMap.COPY_TAG_NAME, 3),
    )


def test_multi_map(tag_map_wth_multi_map):
    assert tag_map_wth_multi_map.map_tags(["+A"]) == ["A+"]
    assert tag_map_wth_multi_map.map_tags(["+B"]) == ["B+"]
    assert tag_map_wth_multi_map.map_tags(["+B", "+A"]) == ["A+", "B+"]
    assert tag_map_wth_multi_map.map_tags(["+A", "+B"]) == ["abc+"]


@pytest.fixture
def tag_map_with_default():
    return TagMap(("+A", TagMap.COPY_TAG_NAME, 1), (TagMap.DEFAULT, "+B", 1))


def test_use_default(tag_map_with_default):
    assert tag_map_with_default.map_tags(["+A"]) == ["A+"]
    assert tag_map_with_default.map_tags([]) == ["+B"]


def test_can_supply_multiple_defaults():
    with pytest.raises(
        Exception,
        match=re.escape("multiple defaults supplied for precedence 1: +A, +B"),
    ):
        TagMap((TagMap.DEFAULT, "+A", 1), (TagMap.DEFAULT, "+B", 1))


## Test features used by EIP


@pytest.fixture
def tag_map_with_both_plusses_on_left_side():
    return TagMap(("+A", "+B", 1), ("+C", "+X", 2))


def test_tag_map_with_both_plusses_on_left_side(tag_map_with_both_plusses_on_left_side):
    assert tag_map_with_both_plusses_on_left_side.map_tags(["+C", "+A"]) == ["+B", "+X"]


@pytest.fixture
def tag_map_multiple_tags():
    return TagMap(("+A", ("+B", "+C"), 1), ("+X", "+Y", 2))


def test_map_multiple_tag_target(tag_map_multiple_tags):
    assert tag_map_multiple_tags.map_tags(["+X", "+A"]) == [
        "+B",
        "+C",
        "+Y",
    ]
