import re

from django.conf import settings

from morphodict.search.affix import (
    do_source_language_affix_search,
    do_target_language_affix_search,
    query_would_return_too_many_results,
)
from morphodict.search.core import SearchRun
from morphodict.search.cvd_search import do_cvd_search
from morphodict.search.lemma_freq import get_lemma_freq
from morphodict.search.glossary_count import get_glossary_count
from morphodict.search.espt import EsptSearch
from morphodict.search.lookup import fetch_results
from morphodict.search.pos_matches import find_pos_matches
from morphodict.search.query import CvdSearchType
from morphodict.search.types import Result
from morphodict.search.util import first_non_none_value
from morphodict.utils.types import cast_away_optional



def search(
    *,
    query: str,
    include_affixes=True,
    include_auto_definitions=False,
    inflect_english_phrases=False
) -> SearchRun:
    """
    Perform an actual search, using the provided options.

    This class encapsulates the logic of which search methods to try, and in
    which order, to build up results in a SearchRun.
    """
    search_run = SearchRun(
        query=query, include_auto_definitions=include_auto_definitions
    )
    initial_query_terms = search_run.query.query_terms[:]

    if (search_run.query.espt or inflect_english_phrases) and (
        len(initial_query_terms) > 1
    ):
        espt_search = EsptSearch(search_run)
        espt_search.analyze_query()

    if settings.MORPHODICT_ENABLE_CVD:
        cvd_search_type = cast_away_optional(
            first_non_none_value(search_run.query.cvd, default=CvdSearchType.DEFAULT)
        )

        # For when you type 'cvd:exclusive' in a query to debug ONLY CVD results!
        if cvd_search_type == CvdSearchType.EXCLUSIVE:

            def sort_by_cvd(r: Result):
                return r.cosine_vector_distance

            search_run.sort_function = sort_by_cvd
            do_cvd_search(search_run)
            return search_run

    fetch_results(search_run)

    if (
        settings.MORPHODICT_ENABLE_AFFIX_SEARCH
        and include_affixes
        and not query_would_return_too_many_results(search_run.internal_query)
    ):
        do_source_language_affix_search(search_run)
        do_target_language_affix_search(search_run)

    if settings.MORPHODICT_ENABLE_CVD:
        if cvd_search_type.should_do_search() and not is_almost_certainly_cree(
            search_run
        ):
            do_cvd_search(search_run)

    if (search_run.query.espt or inflect_english_phrases) and (
        len(initial_query_terms) > 1
    ):
        espt_search.inflect_search_results()

    find_pos_matches(search_run)
    get_glossary_count(search_run)
    get_lemma_freq(search_run)

    return search_run

CREE_LONG_VOWEL = re.compile("[êîôâēīōā]")

def is_almost_certainly_cree(search_run: SearchRun) -> bool:
    """
    Heuristics intended to AVOID doing an English search.
    """
    query = search_run.query

    # If there is a word with two or more dashes in it, it's probably Cree:
    if any(term.count("-") >= 2 for term in query.query_terms):
        search_run.add_verbose_message(
            "Skipping CVD because query has too many hyphens"
        )
        return True

    if CREE_LONG_VOWEL.search(query.query_string):
        search_run.add_verbose_message("Skipping CVD because query has Cree diacritics")
        return True

    return False
