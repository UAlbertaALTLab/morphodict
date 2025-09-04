from typing import Iterable, Callable, Any, Optional

from django.db.models import prefetch_related_objects

from morphodict.paradigm.preferences import DisplayMode
from crkeng.app.preferences import (
    AnimateEmoji,
    DictionarySource,
    ShowEmoji,
)
from morphodict.lexicon.models import WordformKey
from . import types, presentation
from .query import Query
from .types import Result
from .util import first_non_none_value


VerboseMessage = dict[str, str]


class SearchResults:
    """
    Holds a query and gathers results into a result collection.

    This class does not directly perform searches; for that, see runner.py.
    Instead, it provides an API for various search methods to access the query,
    and to add results to the result collection for future ranking.
    """

    def __init__(self, auto=None, verbose=False, include_auto_definitions=None):
        self.include_auto_definitions = first_non_none_value(
            auto, include_auto_definitions, default=False
        )
        self.verbose = verbose
        self._results = {}
        self._verbose_messages = []

    include_auto_definitions: bool
    _results: dict[WordformKey, types.Result]
    _verbose_messages: list[VerboseMessage]
    verbose: bool
    # Set this to use a custom sort function
    sort_function: Optional[Callable[[Result], Any]] = None

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

        # sort based on cvd
        if self.sort_function is not None:
            results.sort(key=self.sort_function)
        else:
            results.sort(key=lambda x: cvd(x), reverse=True)
        return results

    def presentation_results(
        self,
        display_mode=DisplayMode.default,
        animate_emoji=AnimateEmoji.default,
        show_emoji=ShowEmoji.default,
        dict_source=None,
    ) -> list[presentation.PresentationResult]:
        results = self.sorted_results()
        prefetch_related_objects(
            [r.wordform for r in results if not r.wordform._state.adding],
            "lemma__definitions__citations",
            "definitions__citations",
        )
        return [
            presentation.PresentationResult(
                r,
                search_results=self,
                display_mode=display_mode,
                animate_emoji=animate_emoji,
                show_emoji=show_emoji,
                dict_source=dict_source,
            )
            for r in results
        ]

    def serialized_presentation_results(
        self,
        display_mode=DisplayMode.default,
        animate_emoji=AnimateEmoji.default,
        show_emoji=ShowEmoji.default,
        dict_source=None,
    ):
        results = self.presentation_results(
            display_mode=display_mode,
            animate_emoji=animate_emoji,
            show_emoji=show_emoji,
            dict_source=dict_source,
        )
        serialized = [r.serialize() for r in results]

        def has_definition(r):
            # does the entry itself have a definition?
            if r["definitions"]:
                return True
            # is it a form of a word that has a definition?
            if "lemma_wordform" in r:
                if "definitions" in r["lemma_wordform"]:
                    if r["lemma_wordform"]["definitions"]:
                        return True
            return False

        return [r for r in serialized if has_definition(r)]

    def add_verbose_message(self, message: Optional[str] = None, **messages):
        """
        Add any arbitrary JSON-serializable data to be displayed to the user at the
        top of the search page, if a search is run with verbose:1.

        Protip! Use keyword arguments as syntactic sugar for adding a dictionary, e.g.,

            search_results.add_verbose_message(foo="bar")

        Will appear as:

        [
            {"foo": "bar"}
        ]
        """
        if message is None and not messages:
            raise TypeError("must provide a message or messages")

        if message is not None:
            self._verbose_messages.append(dict({"message": message}))
        if messages:
            self._verbose_messages.append(messages)

    @property
    def verbose_messages(self):
        return self._verbose_messages

    def __repr__(self):
        return f"SearchResults<query={self.query!r}>"


def cvd(val):
    return val.relevance_score or 0.0
