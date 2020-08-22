import typing

from django.db import models
from sortedcontainers import SortedSet

if typing.TYPE_CHECKING:
    # Avoid runtime circular-dependency
    # without this line,
    # search_mixin.py
    #   would depend on search.py
    #   which depends on models.py
    #   which depends on search_mixin.py 💥
    from .search import SearchResult


class WordformSearchMixin:
    """
    To be mixed in with a WordformManager to provide this functionality:

        Wordform.objects.search()
    """

    def search(self, query: str, **constraints) -> SortedSet["SearchResult"]:
        from .models import WordformSearch

        search = WordformSearch(query, constraints)
        return search.perform()


class WordformManager(models.Manager, WordformSearchMixin):
    """
    Adds search to wordforms.
    """