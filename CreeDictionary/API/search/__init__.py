from sortedcontainers import SortedSet

from .lookup import (
    WordformSearchWithAffixes,
    WordformSearchWithExactMatch,
)
from .types import SearchResult


def search_with_affixes(
    query: str, include_auto_definitions=False
) -> SortedSet[SearchResult]:
    """
    Search for wordforms matching:
     - the wordform text
     - the definition keyword text
     - affixes of the wordform text
     - affixes of the definition keyword text
    """

    search = WordformSearchWithAffixes(query)
    return search.perform(include_auto_definitions=include_auto_definitions)


def simple_search(
    query: str, include_auto_definitions=False
) -> SortedSet[SearchResult]:
    """
    Search, trying to match full wordforms or keywords within definitions.

    Does NOT try to match affixes!
    """

    search = WordformSearchWithExactMatch(query)
    return search.perform(include_auto_definitions=include_auto_definitions)
