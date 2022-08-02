import json
import logging

import pytest
from hypothesis import assume, given

from CreeDictionary.API.search import search
from CreeDictionary.API.search.util import to_sro_circumflex
from CreeDictionary.tests.conftest import lemmas
from morphodict.lexicon.models import Wordform


@pytest.mark.django_db
def test_when_linguistic_breakdown_absent():
    # pê- is a preverb
    # it's not analyzable by the normative fst and should not have a linguistic breakdown
    # however, in the latest version of the descriptive FST pê- can get analyzed as a fragment, receiving the +Err/Frag tag.
    # nevertheless, currently we ignore the +Err/Frag cases.

    query = "pe-"
    search_results = search(query=query).presentation_results()

    # when introducing cosine vector distance, `pe` is in the news vectors, so
    # we now get additional results for this search.
    assert len(search_results) >= 1

    result = search_results[0]
    assert result.wordform.text == "pê-"
    assert result.wordform.analysis is None
    assert result.friendly_linguistic_breakdown_head == []
    assert (
        result.serialize()["lemma_wordform"]["inflectional_category_plain_english"]
        == "like: pê-"
    )


@pytest.mark.django_db
@given(lemma=lemmas())
def test_query_exact_wordform_in_database(lemma: Wordform):
    """
    Sanity check: querying a lemma by its EXACT text returns that lemma.
    """

    query = lemma.text
    results = search(query=query).presentation_results()

    exact_match = False
    matched_lemma_count = 0
    for r in results:
        if r.wordform.id == lemma.id:
            exact_match = True
        matched_lemma_count += 1

    assert matched_lemma_count >= 1, f"Could not find {query!r} in the database"
    assert exact_match, f"No exact matches for {query!r} in {results}"


@pytest.mark.django_db
@given(lemma=lemmas())
def test_search_for_exact_lemma(lemma: Wordform):
    """
    Check that we get a search result that matches the exact query.
    """

    assert lemma.is_lemma
    _, fst_lemma, _ = lemma.analysis
    assert all(c == c.lower() for c in fst_lemma)
    assume(lemma.text == fst_lemma)

    query = lemma.text
    search_results = search(query=query).presentation_results()

    exact_matches = {
        result
        for result in search_results
        if result.is_lemma and result.lemma_wordform == lemma
    }
    assert len(exact_matches) == 1

    # Let's look at that search result in more detail
    exact_match = exact_matches.pop()
    assert exact_match.source_language_match == lemma.text
    assert not exact_match.preverbs
    # todo: enable the two lines below when #230 is fixed
    #   https://github.com/UAlbertaALTLab/morphodict/issues/230
    #   or there will be flaky local tests and ci tests
    # assert len(exact_match.definitions) >= 1
    # assert all(len(dfn.source_ids) >= 1 for dfn in exact_match.definitions)


@pytest.mark.django_db
def test_search_for_english() -> None:
    """
    Search for a word that is definitely in English.
    """

    # This should match "âcimowin" and related words:
    search_results = search(query="story").presentation_results()

    assert any(r.wordform.text == "âcimowin" for r in search_results)


@pytest.mark.django_db
def test_compare_simple_vs_affix_search() -> None:
    """
    Searches can include affixes or not; by default, they do.

    The only difference is that there should be more things returned via affix search.
    """

    # The prefix should be a complete wordform, as well as a valid prefix of the lemma
    # AA: Is this true? As one can search with an incomplete wordform and get results, e.g. 'wâpamê'

    prefix = "wâpam"
    lemma = "wâpamêw"
    assert lemma.startswith(prefix)

    simple_results = search(query=prefix, include_affixes=False).presentation_results()
    general_results = search(query=prefix).presentation_results()

    assert len(simple_results) <= len(general_results)

    assert results_contains_wordform(prefix, simple_results)
    assert not results_contains_wordform(lemma, simple_results)

    assert results_contains_wordform(prefix, general_results)
    assert results_contains_wordform(lemma, general_results)


@pytest.mark.django_db
def test_search_for_pronoun() -> None:
    """
    Search for a common pronoun "ôma". Make sure "oma" returns at least one
    result that says "ôma"
    """

    search_results = search(query="oma").presentation_results()
    assert any(r.wordform.text == "ôma" for r in search_results)


@pytest.mark.django_db
def test_search_for_stored_non_lemma():
    """
    A "stored non-lemma" is a wordform in the database that is NOT a lemma.
    """
    # "S/he would tell us stories."
    lemma_str = "âcimêw"
    query = "ê-kî-âcimikoyâhk"
    search_results = search(query=query).presentation_results()

    assert len(search_results) >= 1

    exact_matches = [
        result for result in search_results if result.wordform.text == query
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
    See: https://github.com/UAlbertaALTLab/morphodict/issues/147
    """

    # Ensure the word is in the database to begin with...
    word = Wordform.objects.get(text=term)
    assert word is not None

    # Now try searching for it:
    cree_results = search(query=term).presentation_results()
    assert len(cree_results) > 0


@pytest.mark.django_db
@pytest.mark.parametrize("query", ["nipaw", "nitawi", "nitawi-nipaw", "e-nitawi-nipaw"])
def test_search_serialization_json_parsable(query):
    """
    Test serialize produces json compatible results
    """
    results = search(query=query).serialized_presentation_results()
    try:
        json.dumps(results)
    except Exception as e:
        pytest.fail("SearchResult.serialized method failed to be json compatible")
        raise


@pytest.mark.django_db
def test_search_words_with_preverbs():
    """
    preverbs should be extracted and present in SearchResult instances
    """
    results = search(query="nitawi-nipâw").presentation_results()
    assert len(results) == 1
    search_result = results.pop()

    assert len(search_result.preverbs) == 1
    assert search_result.preverbs[0]["text"] == "nitawi-"
    assert search_result.lexical_info[0]["type"] == "Preverb"


@pytest.mark.django_db
def test_search_words_with_reduplication():
    """
    reduplication should be extracted and present in SearchResult instances
    """
    results = search(query="nanipâw").presentation_results()
    assert len(results) == 1
    search_result = results.pop()

    assert len(search_result.lexical_info) == 1
    assert search_result.lexical_info[0]["entry"]["text"] == "na-"
    assert search_result.lexical_info[0]["type"] == "Reduplication"


@pytest.mark.django_db
def test_search_words_with_inital_change():
    """
    reduplication should be extracted and present in SearchResult instances
    """
    results = search(query="nêpat").presentation_results()
    assert len(results) == 1
    search_result = results.pop()

    assert len(search_result.lexical_info) == 1
    assert search_result.lexical_info[0]["entry"]["text"] == " "
    assert search_result.lexical_info[0]["type"] == "Initial Change"


@pytest.mark.django_db
def test_search_text_with_ambiguous_word_classes():
    """
    Results of all word classes should be searched when the query is ambiguous
    """
    # pipon can be viewed as a Verb as well as a Noun
    results = search(query="pipon").presentation_results()
    assert {
        r.lemma_wordform.paradigm for r in results if r.wordform.text == "pipon"
    } == {"NI", "VII"}


@pytest.mark.django_db
def test_lemma_ranking_most_frequent_word():
    # the English sleep should many Cree words. But nipâw should show first because
    # it undoubtedly has the highest frequency
    results = search(query="sees").presentation_results()
    assert results[0].wordform.text == "wâpahtam"


@pytest.mark.django_db
@pytest.mark.parametrize("lemma", ["maskwa", "niska"])
def test_lemma_and_syncretic_form_ranking(lemma):
    """
    Tests that the lemma is always shown first, even when a search yields
    one or more forms that are syncretic with the lemma; That is, ensure THIS
    doesn't happen:

        sheep [Plural]
        form of sheep [Singular]

        (no definition found for sheep [Plural])

        sheep [Singular]
        1. a fluffy mammal that appears in dreams

    Note: this test is likely to be **FLAKY** if the implementation is buggy
    and uses a **non-stable** sort or comparison.
    """

    results = search(query=lemma).presentation_results()
    assert len(results) >= 2
    search_results = [res for res in results if res.lemma_wordform.text == lemma]
    assert len(search_results) >= 2
    assert any(res.is_lemma for res in search_results)
    first_result = search_results[0]
    assert first_result.is_lemma, f"unexpected first result: {first_result}"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "query,top_result,later_result",
    [
        # With long vowel ending (1Sg conjunct)
        ("ê-kotiskâwêyâhk", "ê-kotiskâwêyâhk", "ê-kotiskâwêyahk"),
        # With short vowel ending (2Sg conjunct)
        ("ê-kotiskâwêyahk", "ê-kotiskâwêyahk", "ê-kotiskâwêyâhk"),
        # With long vowel ending (1Sg conjunct)
        ("ᐁᑯᑎᐢᑳᐍᔮᕽ", "ᐁ ᑯᑎᐢᑳᐍᔮᕽ", "ᐁ ᑯᑎᐢᑳᐍᔭᕽ"),
        # With short vowel ending (2Sg conjunct)
        ("ᐁᑯᑎᐢᑳᐍᔭᕽ", "ᐁ ᑯᑎᐢᑳᐍᔭᕽ", "ᐁ ᑯᑎᐢᑳᐍᔮᕽ"),
    ],
)
def test_search_results_order(query: str, top_result: str, later_result: str):
    """
    Ensure that some search results appear before others.
    """
    results = search(query=query).presentation_results()

    top_result_pos = position_in_results(top_result, results)
    later_result_pos = position_in_results(later_result, results)
    assert (
        top_result_pos < later_result_pos
    ), f"{top_result} did not come before {later_result}"


@pytest.mark.django_db
def test_logs_error_on_analyzable_result_without_generated_string(caplog):
    """
    Ensures searching does not crash when given an analyzable result with no normative
    form. An error should be logged instead.

    It used to raise: ValueError: min() arg is an empty sequence

    See: https://github.com/UAlbertaALTLab/morphodict/issues/693
    """
    with caplog.at_level(logging.ERROR):
        search(query="bod").presentation_results()

    errors = [log for log in caplog.records if log.levelname == "ERROR"]
    assert len(errors) >= 1
    assert any("bod" in log.message for log in errors)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "query",
    [
        # typo in pîmi-:
        "ê-pim-nêhiyawêyahk",
        # non-word with plausible Cree phonotactics:
        "pêp-kôniw",  # (see: https://www.youtube.com/watch?v=3fG8rNHUspU)
    ],
)
def test_avoids_cvd_search_if_query_looks_like_cree(query: str) -> None:
    """
    Some searches should not even **TOUCH** CVD, yielding zero results.
    """
    assert search(query=query).verbose_messages[0].startswith("Skipping CVD")


####################################### Helpers ########################################


def position_in_results(wordform_text: str, search_results) -> int:
    """
    Find the EXACT wordform in the results.
    """
    wordform_text = to_sro_circumflex(wordform_text)

    for pos, result in enumerate(search_results):
        if wordform_text == result.wordform.text:
            return pos
    raise AssertionError(f"{wordform_text} not found in results: {search_results}")


def results_contains_wordform(wordform: str, search_results) -> bool:
    """
    Returns True if the wordform is found in the search results.
    """
    return any(r.wordform.text == wordform for r in search_results)
