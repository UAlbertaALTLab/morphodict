from .runner import is_almost_certainly_cree, search, wordnet_search as wordnet_runner
from .core import SearchResults, Result
from .presentation import SerializedPresentationResult
from .query import Query
from .wordnet import WordnetEntry
from morphodict.lexicon.models import RapidWords, WordNetSynset


def search_with_affixes(
    query: str, include_auto_definitions=False, inflect_english_phrases=False
) -> SearchResults:
    """
    Search for wordforms matching:
     - the wordform text
     - the definition keyword text
     - affixes of the wordform text
     - affixes of the definition keyword text
    """

    return search(
        query=query,
        include_auto_definitions=include_auto_definitions,
        inflect_english_phrases=inflect_english_phrases,
    )


def api_search(
    query: str, include_auto_definitions=False, inflect_english_phrases=False
) -> list[SerializedPresentationResult]:
    """
    Search, trying to match full wordforms or keywords within definitions.

    Does NOT try to match affixes!
    """

    return search(
        query=query,
        include_affixes=False,
        include_auto_definitions=include_auto_definitions,
        inflect_english_phrases=inflect_english_phrases,
    ).serialized_presentation_results()


def wordnet_search(query: str) -> list[tuple[WordnetEntry, str, SearchResults]] | None:
    # If we are doing an english simple phrase
    search_query = Query(query)
    if is_almost_certainly_cree(search_query, SearchResults()):
        return None
    return wordnet_runner(search_query)


def rapidwords_index_search(index: str) -> SearchResults | None:
    try:
        rw_category = RapidWords.objects.get(index=index.strip())
        results = SearchResults()
        for word in rw_category.wordforms.all():
            results.add_result(Result(word, rapidwords_match=True))
        return results
    except:
        pass
    return None


def wordnet_index_search(index: str) -> SearchResults | None:
    try:
        wn_category = WordNetSynset.objects.get(name=index.strip())
        results = SearchResults()
        for word in wn_category.wordforms.all():
            results.add_result(Result(word, wordnet_match=True))
        return results
    except:
        pass
    return None
