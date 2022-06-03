import re

from django.conf import settings

from CreeDictionary.API.search.affix import (
    do_source_language_affix_search,
    do_target_language_affix_search,
    query_would_return_too_many_results,
)
from CreeDictionary.API.search.core import SearchRun
from CreeDictionary.API.search.cvd_search import do_cvd_search
from CreeDictionary.API.search.lemma_freq import get_lemma_freq
from CreeDictionary.API.search.word_list_freq import get_word_list_freq
from CreeDictionary.API.search.espt import EsptSearch
from CreeDictionary.API.search.lookup import fetch_results
from CreeDictionary.API.search.pos_matches import find_pos_matches
from CreeDictionary.API.search.query import CvdSearchType
from CreeDictionary.API.search.types import Result
from CreeDictionary.API.search.util import first_non_none_value
from CreeDictionary.utils.types import cast_away_optional

CREE_LONG_VOWEL = re.compile("[êîôâēīōā]")


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

    if search_run.query.espt or inflect_english_phrases:
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

    if search_run.query.espt or inflect_english_phrases:
        espt_search.inflect_search_results()

    find_pos_matches(search_run)
    get_word_list_freq(search_run)
    get_lemma_freq(search_run)

    return search_run


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
