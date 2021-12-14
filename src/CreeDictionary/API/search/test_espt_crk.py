import pytest

from CreeDictionary.API.search.core import SearchRun
from CreeDictionary.API.search.espt import EsptSearch, PhraseAnalyzedQuery
from CreeDictionary.API.search.types import Result
from morphodict.lexicon.models import Wordform


@pytest.mark.parametrize(
    ("query", "has_tags", "tags", "filtered_query"),
    [
        ("atim", False, None, None),
        ("they swam", True, ["+V", "+AI", "+Prt", "+3Pl"], "swim"),
        ("dog +Px1Sg+Sg", False, None, None),
    ],
)
def test_search_with_tags(query, has_tags, tags, filtered_query):
    result = PhraseAnalyzedQuery(query)
    assert result.has_tags == has_tags
    if has_tags:
        assert result.tags == tags
        assert result.filtered_query == filtered_query


@pytest.mark.parametrize(
    ("search", "params"),
    [
        [
            "they crawled",
            {
                "expected_query_terms": ["crawls"],
                "expected_new_tags": ["+V", "+AI", "PV/ki+", "+Ind", "+3Pl"],
                "slug": "pimitâcimow",
                "expected_inflection": "kî-pimitâcimowak",
            },
        ],
        [
            "they saw me",
            {
                "expected_query_terms": ["see"],
                "expected_new_tags": ["+V", "+TA", "PV/ki+", "+Ind", "+3Pl", "+1SgO"],
                "slug": "wâpamêw",
                "expected_inflection": "nikî-wâpamikwak",
            },
        ],
        [
            "my cats",
            {
                "expected_query_terms": ["cat"],
                "expected_new_tags": ["+N", "+Px1Sg", "+Pl"],
                "slug": "minôs",
                "expected_inflection": "niminôsak",
            },
        ],
        [
            "they see",
            {
                "expected_query_terms": ["see"],
                "expected_new_tags": ["+V", "+AI", "+Ind", "+3Pl"],
                "slug": "wâpiw@1",
                "expected_inflection": "wâpiwak",
            },
        ],
        [
            "you ate it",
            {
                "expected_query_terms": ["eat"],
                "expected_new_tags": ["+V", "+TI", "PV/ki+", "+Ind", "+2Sg"],
                "slug": "mîciw",
                "expected_inflection": "kikî-mîcin",
            },
        ],
        [
            "they ran",
            {
                "expected_query_terms": ["run"],
                "expected_new_tags": ["+V", "+AI", "PV/ki+", "+Ind", "+3Pl"],
                "slug": "kotiskâwêw",
                "expected_inflection": "kî-kotiskâwêwak",
            },
        ],
        [
            "bear",
            {
                # Don’t try to inflect results for searches not analyzable as phrases
                "expected_query_terms": ["bear"],
                "expected_new_tags": [],
                "slug": "maskwa@1",
                "expected_inflection": "maskwa",
            },
        ],
    ],
)
def test_espt_search(db, search, params):
    search_run = SearchRun(search)
    espt_search = EsptSearch(search_run)
    espt_search.analyze_query()
    assert search_run.query.query_terms == params["expected_query_terms"]
    assert search_run.query.query_string == " ".join(params["expected_query_terms"])
    assert espt_search.new_tags == params["expected_new_tags"]

    lemma1 = Wordform.objects.get(slug=params["slug"], is_lemma=True)

    search_run.add_result(
        Result(
            wordform=lemma1,
            target_language_keyword_match=params["expected_query_terms"],
        )
    )

    espt_search.inflect_search_results()

    assert params["expected_inflection"] in [
        entry.wordform.text for entry in list(search_run.unsorted_results())
    ]


def test_espt_search_doesnt_crash_when_no_analysis(db):
    search_run = SearchRun("my little bears")
    espt_search = EsptSearch(search_run)
    espt_search.analyze_query()

    wordform = Wordform(text="pê-")
    wordform.lemma = wordform
    wordform.is_lemma = True
    search_run.add_result(
        Result(wordform=wordform, target_language_keyword_match=["bear"])
    )

    # This will crash if the espt code doesn’t handle results without an analysis
    espt_search.inflect_search_results()
