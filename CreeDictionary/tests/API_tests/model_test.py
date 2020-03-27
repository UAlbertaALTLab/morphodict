import json
from collections import Iterable

import pytest
from hypothesis import assume, given

from API.models import Wordform, filter_cw_wordforms
from constants import Language
from CreeDictionary import settings
from tests.conftest import random_lemmas


@pytest.fixture(scope="module")
def django_db_setup():
    """
    This works with pytest-django plugin.
    This fixture tells all functions marked with pytest.mark.django_db in this file
    to use the database specified in settings.py
    which is the existing test_db.sqlite3 if USE_TEST_DB=True is passed.

    Instead of by default, an empty database in memory.
    """

    # all functions in this file should use the existing test_db.sqlite3
    assert settings.USE_TEST_DB


#### Tests for Inflection.fetch_lemmas_by_user_query()


@pytest.mark.django_db
def test_when_linguistic_breakdown_absent():
    # pê- is a preverb
    # it's not analyzable by the fst and should not have a linguistic breakdown

    query = "pe-"
    search_results = Wordform.search(query)

    assert len(search_results) == 1

    result = search_results[0]
    assert (
        result.linguistic_breakdown_head == ()
        and result.linguistic_breakdown_tail == ()
    )


@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_query_exact_wordform_in_database(lemma: Wordform):
    """
    Sanity check: querying a lemma by its EXACT text returns that lemma.
    """

    query = lemma.text
    cree_results, _ = Wordform.fetch_lemma_by_user_query(query)

    exact_match = False
    matched_lemma_count = 0
    for analysis, matched_cree, lemma in cree_results:
        if lemma.id == lemma.id:
            exact_match = True
        matched_lemma_count += 1

    assert matched_lemma_count >= 1, f"Could not find {query!r} in the database"
    assert exact_match, f"No exact matches for {query!r} in {cree_results}"


@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_search_for_exact_lemma(lemma: Wordform):
    """
    Check that we get a search result that matches the exact query.
    """

    assert lemma.is_lemma
    lemma_from_analysis, _, _ = lemma.analysis.partition("+")
    assert all(c == c.lower() for c in lemma_from_analysis)
    assume(lemma.text == lemma_from_analysis)

    query = lemma.text
    search_results = Wordform.search(query)

    exact_matches = {
        result
        for result in search_results
        if result.is_lemma and result.lemma_wordform == lemma
    }
    assert len(exact_matches) == 1

    # Let's look at that search result in more detail
    exact_match = exact_matches.pop()
    assert exact_match.matched_cree == lemma.text
    assert not exact_match.preverbs
    assert not exact_match.reduplication_tags
    assert not exact_match.initial_change_tags
    # todo: enable the two lines below when #230 is fixed
    #   https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/230
    #   or there will be flaky local tests and ci tests
    # assert len(exact_match.definitions) >= 1
    # assert all(len(dfn.source_ids) >= 1 for dfn in exact_match.definitions)


@pytest.mark.django_db
def test_search_for_english() -> None:
    """
    Search for a word that is definitely in English.
    """

    # This should match "âcimowin" and related words:
    search_results = Wordform.search("story")

    assert search_results[0].matched_by == Language.ENGLISH


@pytest.mark.django_db
def test_search_for_pronoun() -> None:
    """
    Search for a common pronoun "ôma". Make sure "oma" returns at least one
    result that says "ôma"
    """

    search_results = Wordform.search("oma")
    assert "ôma" in {res.matched_cree for res in search_results}


@pytest.mark.django_db
def test_search_for_stored_non_lemma():
    """
    A "stored non-lemma" is a wordform in the database that is NOT a lemma.
    """
    # "S/he would tell us stories."
    lemma_str = "âcimêw"
    query = "ê-kî-âcimikoyâhk"
    search_results = Wordform.search(query)

    assert len(search_results) >= 1

    exact_matches = [
        result for result in search_results if result.matched_cree == query
    ]
    assert len(exact_matches) >= 1

    # Let's look at that search result in more detail
    result = exact_matches[0]
    assert not result.is_lemma
    assert result.lemma_wordform.text == lemma_str
    # todo: tags are not implemented
    # assert not result.preverbs
    # assert not result.reduplication_tags
    # assert not result.initial_change_tags
    assert len(result.lemma_wordform.definitions.all()) >= 1
    assert all(
        len(dfn.source_ids) >= 1 for dfn in result.lemma_wordform.definitions.all()
    )


# TODO: some of these should really be in a dedicated "test_search" file.


@pytest.mark.django_db
@pytest.mark.parametrize("term", ["acâhkos kâ-osôsit", "acâhkosa kâ-otakohpit"])
def test_search_space_characters_in_matched_term(term):
    """
    The search should find results with spaces in them.
    See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/147
    """

    # Ensure the word is in the database to begin with...
    word = Wordform.objects.get(text=term)
    assert word is not None

    # Now try searching for it:
    cree_results, _ = Wordform.fetch_lemma_by_user_query(term)
    assert len(cree_results) > 0


@pytest.mark.django_db
def test_paradigm():
    def deep_contain(container: Iterable, testee):
        """check if `testee` is in any depth of `container`"""
        for item in container:
            if item == testee:
                return True
            elif (
                item != container
                and isinstance(item, Iterable)
                and deep_contain(item, testee)
            ):
                return True
        return False

    nipaw_paradigm = Wordform.objects.get(text="nipâw", is_lemma=True).paradigm
    assert deep_contain(nipaw_paradigm, "ninipân")
    assert deep_contain(nipaw_paradigm, "kinipân")
    assert deep_contain(nipaw_paradigm, "nipâw")
    assert deep_contain(nipaw_paradigm, "ninipânân")


@pytest.mark.django_db
@pytest.mark.parametrize("query", ["nipaw", "nitawi", "nitawi-nipaw", "e-nitawi-nipaw"])
def test_search_serialization_json_parsable(query):
    """
    Test SearchResult.serialize produces json compatible results
    """
    results = Wordform.search(query)
    for result in results:

        serialized = result.serialize()
        try:
            json.dumps(serialized)
        except Exception as e:
            print(e)
            pytest.fail("SearchResult.serialized method failed to be json compatible")


@pytest.mark.django_db
def test_search_words_with_preverbs():
    """
    preverbs should be extracted and present in SearchResult instances
    """
    results = Wordform.search("nitawi-nipâw")
    assert len(results) == 1
    search_result = results.pop()

    assert len(search_result.preverbs) == 1
    assert search_result.preverbs[0].text == "nitawi-"


@pytest.mark.django_db
def test_search_text_with_ambiguous_word_classes():
    """
    Results of all word classes should be searched when the query is ambiguous
    """
    # pipon can be viewed as a Verb as well as a Noun
    results = Wordform.search("pipon")
    assert {r.lemma_wordform.pos for r in results if r.matched_cree == "pipon"} == {
        "N",
        "V",
    }


@pytest.mark.django_db
def test_lemma_ranking_most_frequent_word():
    # the English sleep should many cree words. But nipâw should show first because
    # it undoubtedly has the highest frequency
    results = Wordform.search("sleep")
    assert results[0].matched_cree == "nipâw"
