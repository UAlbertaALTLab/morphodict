from typing import Any, Iterable

from django.db.models import prefetch_related_objects

from crkeng.app.preferences import DisplayMode, AnimateEmoji, DictionarySourceMd, DictionarySourceCw
from . import types, presentation
from .query import Query
from .util import first_non_none_value
from morphodict.lexicon.models import Wordform, wordform_cache, WordformKey


class SearchRun:
    """
    Holds a query and gathers results into a result collection.

    This class does not directly perform searches; for that, see runner.py.
    Instead, it provides an API for various search methods to access the query,
    and to add results to the result collection for future ranking.
    """

    def __init__(self, query: str, include_auto_definitions=None):
        self.query = Query(query)
        self.include_auto_definitions = first_non_none_value(
            self.query.auto, include_auto_definitions, default=False
        )
        self._results = {}
        self._verbose_messages = []

    include_auto_definition: bool
    _results: dict[WordformKey, types.Result]
    VerboseMessage = dict[str, str]
    _verbose_messages: list[VerboseMessage]

    def add_result(self, result: types.Result):
        if not isinstance(result, types.Result):
            raise TypeError(f"{result} is {type(result)}, not Result")
        key = result.wordform.key
        if key in self._results:
            self._results[key].add_features_from(result)
        else:
            self._results[key] = result

    def has_result(self, result: types.Result):
        return result.wordform.key in self._results

    def remove_result(self, result: types.Result):
        del self._results[result.wordform.key]

    def unsorted_results(self) -> Iterable[types.Result]:
        return self._results.values()

    def sorted_results(self) -> list[types.Result]:
        results = list(self._results.values())
        for r in results:
            r.assign_default_relevance_score()
        results.sort()
        return results

    def presentation_results(
        self,
        display_mode=DisplayMode.default,
        animate_emoji=AnimateEmoji.default,
        include_md_results=DictionarySourceMd.default,
        include_cw_results=DictionarySourceCw.default
    ) -> list[presentation.PresentationResult]:
        results = self.sorted_results()
        prefetch_related_objects(
            [r.wordform for r in results],
            "lemma__definitions__citations",
            "definitions__citations",
        )
        return [
            presentation.PresentationResult(
                r,
                search_run=self,
                display_mode=display_mode,
                animate_emoji=animate_emoji,
                include_md_results=include_md_results,
                include_cw_results=include_cw_results,
            )
            for r in results
        ]

    def serialized_presentation_results(
        self, display_mode=DisplayMode.default, animate_emoji=AnimateEmoji.default, include_cw_results=DictionarySourceCw.default, include_md_results=DictionarySourceMd.default
    ):
        results = self.presentation_results(
            display_mode=display_mode, animate_emoji=animate_emoji, include_cw_results=include_cw_results, include_md_results=include_md_results
        )
        return [r.serialize() for r in results]

    def add_verbose_message(self, message=None, **messages):
        """
        Add any arbitrary JSON-serializable data to be displayed to the user at the
        top of the search page, if a search is run with verbose:1.

        Protip! Use keyword arguments as syntactic sugar for adding a dictionary, e.g.,

            search_run.add_verbose_message(foo="bar")

        Will appear as:

        [
            {"foo": "bar"}
        ]
        """
        if message is None and not messages:
            raise TypeError("must provide a message or messages")

        if message is not None:
            self._verbose_messages.append(message)
        if messages:
            self._verbose_messages.append(messages)

    @property
    def verbose_messages(self):
        return self._verbose_messages

    @property
    def internal_query(self):
        return self.query.query_string

    def __repr__(self):
        return f"SearchRun<query={self.query!r}>"
