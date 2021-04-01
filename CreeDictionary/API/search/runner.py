from API.search.affix import (
    do_source_language_affix_search,
    do_target_language_affix_search,
    query_would_return_too_many_results,
)
from API.search.core import SearchRun
from API.search.lookup import fetch_results


def search(*, query: str, include_affixes=True, include_auto_definitions=False):
    """
    Perform an actual search, using the provided options.

    This class encapsulates the logic of which search methods to try, and in
    which order, to build up results in a SearchRun.
    """
    search_run = SearchRun(
        query=query, include_auto_definitions=include_auto_definitions
    )

    fetch_results(search_run)

    if include_affixes and not query_would_return_too_many_results(
        search_run.internal_query
    ):
        do_source_language_affix_search(search_run)
        do_target_language_affix_search(search_run)

    return search_run
