import bisect
from typing import Optional, List

from django.db.models import QuerySet

from fuzzy_search.fuzzy_searcher import FuzzySearcher


class OrderedInflectionQuerySet(QuerySet):
    # noinspection PyArgumentList
    def __new__(cls, query_set: QuerySet):
        query_set.get_next_smaller = lambda lookup_string: cls.get_next_smaller(
            query_set, lookup_string
        )
        query_set._unique_sorted_words = query_set.distinct().values_list(
            "text", flat=True
        )
        query_set._unique_count = len(query_set._unique_sorted_words)
        query_set.strings_to_elements = lambda strings: cls.strings_to_elements(
            query_set, strings
        )
        return query_set

    @classmethod
    def from_query_set(
        cls, ordered_inflection_query_set: QuerySet
    ) -> "OrderedInflectionQuerySet":
        return cls(ordered_inflection_query_set)

    def get_next_smaller(self, this_string: str) -> Optional[str]:
        pos = bisect.bisect_left(self._unique_sorted_words, this_string)

        if pos < self._unique_count:
            return self._unique_sorted_words[pos]
        else:
            return None

    def strings_to_elements(self, results: List[str]) -> QuerySet:
        """
        how to convert the result strings to the
        """
        return self.filter(text__in=results)


class CreeFuzzySearcher(FuzzySearcher):
    def __init__(self, inflections: QuerySet):
        super().__init__(CreeFuzzySearcher._load_sorted_from_db(inflections))

    @staticmethod
    def _load_sorted_from_db(inflections) -> OrderedInflectionQuerySet:
        return OrderedInflectionQuerySet.from_query_set(inflections.order_by("text"))
