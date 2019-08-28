from typing import Iterable

import pytest

from API.models import Inflection
from fuzzy_search.cree_fuzzy_search import CreeFuzzySearcher


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("corpus", "query", "distance", "expected"),
    (
        [("a", "b", "c"), "a", 1, (0, 1, 2)],
        [("a", "bb", "c"), "a", 1, (0, 2)],
        [("a", "ab", "c"), "a", 1, (0, 1, 2)],
        [("a", "ab", "c"), "ab", 1, (0, 1)],
        [("banana", "bapapa", "papapa"), "banana", 2, (0, 1)],
    ),
)
def test_search(
    corpus: Iterable[str], query: str, distance: int, expected: Iterable[int]
):
    for i, word in enumerate(corpus):
        Inflection(id=i, text=word, analysis="", is_lemma=True, as_is=True).save()

    fuzzy_searcher = CreeFuzzySearcher()
    assert set(fuzzy_searcher.search(query, distance)) == set(
        Inflection.objects.filter(id__in=expected)
    )
    # CreeFuzzySearcher is a singleton class. Destroy the created instance
    assert CreeFuzzySearcher() is fuzzy_searcher
    CreeFuzzySearcher._instance = None
