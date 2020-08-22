import typing

from django.db import models
from sortedcontainers import SortedSet

if typing.TYPE_CHECKING:
    # Avoid runtime circular-dependency
    # without this line,
    # wordform_manager_with_search.py
    #   would depend on search.py
    #   which depends on models.py
    #   which depends on wordform_manager_with_search.py 💥
    from .search import SearchResult


class WordformManagerWithSearch(models.Manager):
    """
    Adds Search to Wordform objects:

        Wordform.objects.search()
    """

    def search(self, query: str, **constraints) -> SortedSet["SearchResult"]:
        from .search import WordformSearch

        search = WordformSearch(query, constraints)
        return search.perform()
