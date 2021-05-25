import pytest

from CreeDictionary.API.search.eip import PhraseAnalyzedQuery


@pytest.mark.parametrize(
    ("query", "has_tags", "tags", "filtered_query"),
    [
        ("atim", False, None, None),
        ("they swam", True, ["+V", "+AI", "+Prt", "+3Pl"], "swim"),
        ("dog +Px1Sg+Sg", False, None, None)
    ]
)
def test_search_with_tags(query, has_tags, tags, filtered_query):
    result = PhraseAnalyzedQuery(query)
    assert result.has_tags == has_tags
    if has_tags:
        assert result.tags == tags
        assert result.filtered_query == filtered_query

