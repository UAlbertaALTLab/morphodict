import pytest
from hypothesis import assume, given

from API.models import Wordform, filter_cw_wordforms
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
@given(lemma=random_lemmas())
def test_query_exact_wordform_in_database(lemma: Wordform):
    """
    Sanity check: querying a lemma by its EXACT text returns that lemma.
    """

    query = lemma.text
    analysis_to_lemmas, _ = Wordform.fetch_lemma_by_user_query(query)

    exact_match = False
    matched_lemma_count = 0
    for analysis, lemmas in analysis_to_lemmas.items():
        for matched_lemma in lemmas:
            if matched_lemma.id == lemma.id:
                exact_match = True
            matched_lemma_count += 1

    assert matched_lemma_count >= 1, f"Could not find {query!r} in the database"
    assert exact_match, f"No exact matches for {query!r} in {analysis_to_lemmas}"


# fixme: Eddie
@pytest.mark.skip(reason="Eddies unfinished search code")
@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_search_for_exact_lemma(lemma: Wordform):
    """
    Check that we get a search result that matches the exact query.
    """

    assert lemma.is_lemma
    # XXX: there is something weird where a lemma is not a lemma...
    # bug in the FST? bug in the dictionary? Either way, it's inconvenient.
    lemma_from_analysis, _, _ = lemma.analysis.partition("+")
    assert all(c == c.lower() for c in lemma_from_analysis)
    assume(lemma.text == lemma_from_analysis)

    query = lemma.text
    matched_language, search_results = Wordform.search(query)

    assert matched_language == "crk", "We should have gotten results for Cree"

    exact_matches = [
        result for result in search_results if result.wordform == lemma.text
    ]
    assert len(exact_matches) >= 1

    # Let's look at that search result in more detail
    result = exact_matches[0]
    assert result.wordform == lemma.text
    assert result.is_lemma
    assert result.lemma == lemma.text
    assert not result.preverbs
    assert not result.reduplication_tags
    assert not result.initial_change_tags
    assert len(result.definitions) >= 1
    assert all(len(dfn.source_ids) >= 1 for dfn in result.definitions)


@pytest.mark.skip(reason="The test DB does not contain matching English content :/")
@pytest.mark.django_db
def test_search_for_english() -> None:
    """
    Search for a word that is definitely in English.
    """

    # This should match "âcimowin" and related words:
    matched_language, search_results = Wordform.search("story")

    assert matched_language == "en"


@pytest.mark.django_db
def test_search_for_stored_non_lemma():
    """
    A "stored non-lemma" is a wordform in the database that is NOT a lemma.
    """
    # "S/he would tell us stories."
    lemma = "âcimêw"
    query = "ê-kî-âcimikoyâhk"
    matched_language, search_results = Wordform.search(query)

    assert matched_language == "crk", "We should have gotten results for Cree"
    assert len(search_results) >= 1

    exact_matches = [result for result in search_results if result.wordform == query]
    assert len(exact_matches) >= 1

    # Let's look at that search result in more detail
    result = exact_matches[0]
    assert result.wordform == query
    assert not result.is_lemma
    assert result.lemma == lemma
    assert not result.preverbs
    assert not result.reduplication_tags
    assert not result.initial_change_tags
    assert len(result.definitions) >= 1
    assert all(len(dfn.source_ids) >= 1 for dfn in result.definitions)


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
    analysis_to_lemmas, _ = Wordform.fetch_lemma_by_user_query(term)
    assert len(analysis_to_lemmas) > 0


@pytest.mark.django_db
def test_filter_cw_content():
    # test 1
    # assumptions
    mowew_queryset = Wordform.objects.filter(text="mowêw", is_lemma=True)
    assert mowew_queryset.count() == 1
    assert {
        ("s/he eats s.o. (e.g. bread)", "CW"),
        ("1. That's where he scolds from. (A location). 2. He scolds about it.", "MD"),
        ("s/he eats s.o. (e.g. bread)", "MD"),
        ("All of you eat it. Animate. [Command]", "MD"),
    } == {
        tuple(definition_dict.values())
        for definition_dict in mowew_queryset.get()
        .definitions.all()
        .values("text", "citations")
    }

    # test 2
    # assumption
    nipa_queryset = Wordform.objects.filter(text="nipa", full_lc="IPV")
    assert (
        nipa_queryset.count() == 1
    )  # there should only be one preverb meaning "during the night", it's from MD

    # test
    filtered = filter_cw_wordforms(nipa_queryset)
    assert (
        len(list(filtered)) == 0
    )  # nipa should no longer be there because the preverb nipa is a MD only word
