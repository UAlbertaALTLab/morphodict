import os

import pytest
from hypothesis import assume, given

from API.models import Wordform, filter_cw_wordforms
from CreeDictionary import settings
from CreeDictionary.settings import BASE_DIR
from tests.conftest import random_lemmas


@pytest.fixture(scope="module")
def django_db_setup():
    """
    django_db_setup is a magic function that works with pytest-django plugin. This fixture automatically works on
    all functions in this file who is labeled with pytest.mark.django_db. These functions will use the existing
    test_db.sqlite3. Instead of by default, an empty database in memory.
    """
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
    }


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


@pytest.mark.django_db
def test_filter_cw_content():
    # assumptions
    # print(settings.DATABASES)
    # print("bobo:", Wordform.objects.all().count())
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
        .definition_set.all()
        .values("text", "citations")
    }

    # test
    filtered = filter_cw_wordforms(mowew_queryset)
    assert (
        len(list(filtered)) == 1
    )  # mowew should still be there because mowew has definition from cw
