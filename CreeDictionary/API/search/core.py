from typing import Union

from django.db.models import prefetch_related_objects

from API.models import Wordform
from . import types, presentation, ranking
from .query import Query
from .util import first_non_none_value

# This type is the int pk for a saved wordform, or (text, analysis) for an unsaved one.
WordformKey = Union[int, tuple[str, str]]


def _wordform_key(wordform: Wordform) -> WordformKey:
    if wordform.id is not None:
        return wordform.id
    return (wordform.text, wordform.analysis)


class SearchRun:
    """
    Holds a query and gathers results into a result collection.

    This class does not directly perform searches; for that, see runner.py.
    Instead, it provides an API for various search methods to access the query,
    and to add results to the result collection for future ranking.
    """

    def __init__(self, query: str, include_auto_definitions=None):
        self.query = Query(query)
        self.internal_query = self.query.query_string
        self.include_auto_definitions = first_non_none_value(
            self.query.auto, include_auto_definitions, default=False
        )
        self._results = {}

    include_auto_definition: bool
    _results: dict[WordformKey, types.Result]

    def add_result(self, result: types.Result):
        if not isinstance(result, types.Result):
            raise TypeError(f"{result} is {type(result)}, not Result")
        key = _wordform_key(result.wordform)
        if key in self._results:
            self._results[key].add_features_from(result)
        else:
            self._results[key] = result

    def presentation_results(self) -> list[presentation.PresentationResult]:
        results = list(self._results.values())
        results.sort(key=ranking.sort_by_user_query(self))
        try:
            prefetch_related_objects(
                [r.wordform for r in results],
                "lemma__definitions__citations",
                "definitions__citations",
            )
        except AttributeError:
            # This happens rarely, but is reproducible with the test suite:
            # “'RelatedManager' object has no attribute 'citations'.” I think
            # this is a django bug? It tries to look up a field from Definition
            # on a DictionarySource object. Passing on the exception just means
            # that some searches will run more slowly. To revisit when upgrading
            # to Django 3.
            pass
        return [presentation.PresentationResult(r, search_run=self) for r in results]

    def serialized_presentation_results(self):
        return [r.serialize() for r in self.presentation_results()]

    def __str__(self):
        return f"SearchRun<query={self.query}>"
