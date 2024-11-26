import re

from django.conf import settings

from morphodict.search.affix import (
    do_source_language_affix_search,
    do_target_language_affix_search,
    query_would_return_too_many_results,
)
from morphodict.search.core import SearchResults
from morphodict.search.cvd_search import do_cvd_search
from morphodict.search.lemma_freq import get_lemma_freq
from morphodict.search.glossary_count import get_glossary_count
from morphodict.search.espt import EsptSearch
from morphodict.search.lookup import fetch_results
from morphodict.search.pos_matches import find_pos_matches
from morphodict.search.query import CvdSearchType, Query
from morphodict.search.types import Result
from morphodict.search.util import first_non_none_value


def search(
    query: str,
    include_affixes=True,
    include_auto_definitions=False,
    inflect_english_phrases=False,
) -> SearchResults:
    """
    Perform an actual search, using the provided options.

    This class encapsulates the logic of which search methods to try, and in
    which order, to build up results in a SearchResults object.
    """

    search_query = Query(query)

    search_results = SearchResults(
        auto=search_query.auto,
        verbose=search_query.verbose,
        include_auto_definitions=include_auto_definitions,
    )

    initial_query_terms = search_query.query_terms[:]

    # If we need to do english simple phrase search
    espt_search = None
    if (search_query.espt or inflect_english_phrases) and (
        len(initial_query_terms) > 1
    ):
        espt_search = EsptSearch(search_query, search_results)
        espt_search.convert_search_query_to_espt()

    # Now, check if we were asked to do only vector distance results, and if so,
    # compute them and return them:
    if settings.MORPHODICT_ENABLE_CVD:
        cvd_search_type: CvdSearchType = first_non_none_value(
            search_query.cvd, default=CvdSearchType.DEFAULT
        )

        # For when you type 'cvd:exclusive' in a query to debug ONLY CVD results!
        if cvd_search_type == CvdSearchType.EXCLUSIVE:

            def sort_by_cvd(r: Result):
                return r.cosine_vector_distance

            search_results.sort_function = sort_by_cvd
            do_cvd_search(search_query, search_results)
            return search_results

    # We were NOT asked for only vector distance results, so now we actually
    # go and perform the search.

    # First, fetch keyword-based and FST-based orthography-relaxed results
    fetch_results(search_query, search_results)

    # If allowed, add affix search candidates
    if (
        settings.MORPHODICT_ENABLE_AFFIX_SEARCH
        and include_affixes
        and not query_would_return_too_many_results(search_query.query_string)
    ):
        do_source_language_affix_search(search_query, search_results)
        do_target_language_affix_search(search_query, search_results)

    # Now, if we wanted to do vector search (not exclusively), add the results.
    if settings.MORPHODICT_ENABLE_CVD:
        if cvd_search_type.should_do_search() and not is_almost_certainly_cree(
            search_query, search_results
        ):
            do_cvd_search(search_query, search_results)

    # If we did an english phrase search, we have to inflect back the results!
    if (search_query.espt or inflect_english_phrases) and (
        len(initial_query_terms) > 1
    ):
        espt_search.inflect_search_results()

    # Annotate every entry in search results with the POS match when that is available 
    if espt_search:
        find_pos_matches(espt_search, search_results)
    
    # Annotate every entry with a frequency count from the glossary
    get_glossary_count(search_results)

    # Annotate every entry with a lemma frequency from lemma_frequency.txt
    get_lemma_freq(search_results)

    # Return. NOTE THAT WE HAVE NOT SORTED RESULTS YET!
    # This will be done when we call sorted_results
    return search_results


CREE_LONG_VOWEL = re.compile("[êîôâēīōā]")


def is_almost_certainly_cree(query: Query, search_results: SearchResults) -> bool:
    """
    Heuristics intended to AVOID doing an English search.
    """

    # If there is a word with two or more dashes in it, it's probably Cree:
    if any(term.count("-") >= 2 for term in query.query_terms):
        search_results.add_verbose_message(
            "Skipping CVD because query has too many hyphens"
        )
        return True

    if CREE_LONG_VOWEL.search(query.query_string):
        search_results.add_verbose_message(
            "Skipping CVD because query has Cree diacritics"
        )
        return True

    return False
