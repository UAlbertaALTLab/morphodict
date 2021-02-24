import pytest

from phrase_translate.tag_map import TagMap


@pytest.fixture
def simple_tag_map():
    return TagMap(("+A", "abc+", 1))


def test_simple_tag_map(simple_tag_map):
    assert simple_tag_map.map_tags(["+A"]) == ["abc+"]


def test_raises_on_unknown_tag(simple_tag_map):
    with pytest.raises(Exception):
        simple_tag_map.map_tags(["+foo"])


@pytest.fixture
def tag_map_with_precedence():
    return TagMap(("+A", "abc+", 1), ("+B", "copy", 2), ("+C", None, 0))


def test_map_with_precedence(tag_map_with_precedence):
    # No matter what order the input tags, the mapped tags should come out in
    # the order defined by precedence
    assert tag_map_with_precedence.map_tags(["+A", "+B"]) == ["abc+", "B+"]
    assert tag_map_with_precedence.map_tags(["+B", "+A"]) == ["abc+", "B+"]


def test_mapping_to_none(tag_map_with_precedence):
    assert tag_map_with_precedence.map_tags(["+C"]) == []


@pytest.fixture
def tag_map_with_multiples():
    return TagMap(("+A", "copy", 1), ("+A2", "A+", 1), ("+B", "copy", 2))


def test_dedupe(tag_map_with_multiples):
    assert tag_map_with_multiples.map_tags(["+A", "+A2"]) == ["A+"]
    assert tag_map_with_multiples.map_tags(["+A", "+B", "+A2"]) == ["A+", "B+"]


@pytest.fixture
def tag_map_wth_multi_map():
    return TagMap((("+A", "+B"), "abc+", 1), ("+A", "copy", 2), ("+B", "copy", 3))


def test_multi_map(tag_map_wth_multi_map):
    assert tag_map_wth_multi_map.map_tags(["+A"]) == ["A+"]
    assert tag_map_wth_multi_map.map_tags(["+B"]) == ["B+"]
    assert tag_map_wth_multi_map.map_tags(["+B", "+A"]) == ["A+", "B+"]
    assert tag_map_wth_multi_map.map_tags(["+A", "+B"]) == ["abc+"]
