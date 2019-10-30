import pytest
from hypothesis import assume, given
from hypothesis.strategies import from_regex

from API.models import Inflection
from constants import LC
from DatabaseManager.__main__ import cmd_entry
from DatabaseManager.xml_importer import import_xmls
# don not remove theses lines. Stuff gets undefined
# noinspection PyUnresolvedReferences
from tests.conftest import (one_hundredth_xml_dir, random_inflections,
                            random_lemmas, topmost_datadir)
from utils import fst_analysis_parser


# this very cool fixture provides the tests in this file with a database that's imported from one hundreths of the xml
@pytest.fixture(autouse=True, scope="module")
def hundredth_test_database(one_hundredth_xml_dir, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        import_xmls(one_hundredth_xml_dir, verbose=False)
        yield
        cmd_entry([..., "clear"])


#### Tests for Inflection.fetch_lemmas_by_user_query()


@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_query_exact_wordform_in_database(lemma: Inflection):
    """
    Sanity check: querying a lemma by its EXACT text returns that lemma.
    """

    query = lemma.text
    analysis_to_lemmas, _ = Inflection.fetch_lemma_by_user_query(query)

    exact_match = False
    matched_lemma_count = 0
    for analysis, lemmas in analysis_to_lemmas.items():
        for matched_lemma in lemmas:
            if matched_lemma.id == lemma.id:
                exact_match = True
            matched_lemma_count += 1

    assert matched_lemma_count >= 1, f"Could not find {query!r} in the database"
    assert exact_match, f"No exact matches for {query!r} in {analysis_to_lemmas}"


@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_search_for_exact_lemma(lemma: Inflection):
    """
    Check that we get a search result that matches the exact query.
    """
    assert lemma.is_lemma
    query = lemma.text

    matched_language, search_results = Inflection.search(query)

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


@pytest.mark.skip(reason="The test DB does not contain matching English content :/")
@pytest.mark.django_db
def test_search_for_english() -> None:
    """
    Search for a word that is definitely in English.
    """

    # This should match "âcimowin" and related words:
    matched_language, search_results = Inflection.search("story")

    assert matched_language == "en"


@pytest.mark.django_db
def test_search_for_stored_non_lemma():
    """
    A "stored non-lemma" is a wordform in the database that is NOT a lemma.
    """
    # "S/he would tell us stories."
    lemma = "âcimêw"
    query = "ê-kî-âcimikoyâhk"
    matched_language, search_results = Inflection.search(query)

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
