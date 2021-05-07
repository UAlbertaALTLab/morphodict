from operator import attrgetter

from django.db.models import prefetch_related_objects

from . import types, presentation, ranking
from .query import Query
from .ranking import assign_relevance_score
from .util import first_non_none_value
from ..models import WordformKey, Wordform


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
        key = result.wordform.key
        if key in self._results:
            self._results[key].add_features_from(result)
        else:
            self._results[key] = result

    def sorted_results(self) -> list[types.Result]:
        results = list(self._results.values())

        for r in self._results.values():
            assign_relevance_score(r)
        results.sort(key=attrgetter("relevance_score"))
        results.reverse()

        return results

    def presentation_results(self) -> list[presentation.PresentationResult]:
        results = self.sorted_results()
        prefetch_related_objects(
            [r.wordform for r in results],
            "lemma__definitions__citations",
            "definitions__citations",
        )
        return [presentation.PresentationResult(r, search_run=self) for r in results]

    def serialized_presentation_results(self):
        results = self.presentation_results()
        wordforms = [r.wordform for r in results] + [r.wordform.lemma for r in results]

        Wordform.bulk_homograph_disambiguate(
            [wf for wf in wordforms if wf.is_lemma and wf.id is not None]
        )

        return [r.serialize() for r in results]

    def __repr__(self):
        return f"SearchRun<query={self.query!r}>"
