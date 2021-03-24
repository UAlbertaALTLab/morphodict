"""
Affix search

This was originally intended to suggest compound words, so that searching for
‘nipâw’ would also return ‘maci-nipâw’.

But the current implementation, developed as a step towards that, is more like
tab-completion. It uses tries to expand queries, so that searching for ‘snowm’
also returns results for ‘snowmobile’
"""

from collections import defaultdict
from functools import cached_property
from itertools import chain
from typing import Dict, Iterable, List, NewType, Tuple

import dawg
from django.conf import settings

from API.models import Wordform, EnglishKeyword
from utils.cree_lev_dist import remove_cree_diacritics
from .types import (
    EnglishResult,
    MatchedEnglish,
    CreeResult,
    InternalForm,
)

# A simplified form intended to be used within the affix search trie.
SimplifiedForm = NewType("SimplifiedForm", str)


class AffixSearcher:
    """
    Enables prefix and suffix searches given a list of words and their wordform IDs.
    """

    # TODO: "int" should be Wordform PK type

    def __init__(self, words: Iterable[Tuple[str, int]]):
        self.text_to_ids: Dict[str, List[int]] = defaultdict(list)

        words_marked_for_indexing = [
            (simplified_text, wordform_id)
            for raw_text, wordform_id in words
            if (simplified_text := self.to_simplified_form(raw_text))
        ]

        for text, wordform_id in words_marked_for_indexing:
            self.text_to_ids[self.to_simplified_form(text)].append(wordform_id)

        self._prefixes = dawg.CompletionDAWG(
            [text for text, _ in words_marked_for_indexing]
        )
        self._suffixes = dawg.CompletionDAWG(
            [_reverse(text) for text, _ in words_marked_for_indexing]
        )

    def search_by_prefix(self, prefix: str) -> Iterable[int]:
        """
        :return: an iterable of Wordform IDs that match the prefix
        """
        term = self.to_simplified_form(prefix)
        matched_words = self._prefixes.keys(term)
        return chain.from_iterable(self.text_to_ids[t] for t in matched_words)

    def search_by_suffix(self, suffix: str) -> Iterable[int]:
        """
        :return: an iterable of Wordform IDs that match the suffix
        """
        term = self.to_simplified_form(suffix)
        matched_reversed_words = self._suffixes.keys(_reverse(term))
        return chain.from_iterable(
            self.text_to_ids[_reverse(t)] for t in matched_reversed_words
        )

    @staticmethod
    def to_simplified_form(query: str) -> SimplifiedForm:
        """
        Convert to a simplified form of the word and its orthography to facilitate affix
        search.  You SHOULD throw out diacritics, choose a Unicode Normalization form,
        and choose a single letter case here!
        """
        # TODO: make this work for not just Cree!
        # TODO: allow users to override this method
        return SimplifiedForm(remove_cree_diacritics(query.lower()))


def _reverse(text: SimplifiedForm) -> SimplifiedForm:
    return SimplifiedForm(text[::-1])


def do_affix_search(query: InternalForm, affixes: AffixSearcher) -> Iterable[Wordform]:
    """
    Augments the given set with results from performing both a suffix and prefix search on the wordforms.
    """
    matched_ids = set(affixes.search_by_prefix(query))
    matched_ids |= set(affixes.search_by_suffix(query))
    return Wordform.objects.filter(id__in=matched_ids)


def do_english_affix_search(query, english_results):
    english_keywords_matching_affix = do_affix_search(
        query,
        cache.english_affix_searcher,
    )
    for word in english_keywords_matching_affix:
        english_results.add(EnglishResult(MatchedEnglish(query), word, word.lemma))


def do_cree_affix_seach(query, cree_results):
    cree_words_matching_affix = do_affix_search(
        query,
        cache.cree_affix_searcher,
    )
    for word in cree_words_matching_affix:
        cree_results.add(CreeResult.from_wordform(word))


def query_would_return_too_many_results(query: InternalForm) -> bool:
    """
    If we do an search on too short an affix, the tries will match
    WAY too many results.
    """
    return len(query) <= settings.AFFIX_SEARCH_THRESHOLD


def fetch_english_keywords_with_ids():
    """
    Return pairs of indexed English keywords with their corresponding Wordform IDs.
    """
    return EnglishKeyword.objects.all().values_list("text", "lemma__id")


def fetch_cree_lemmas_with_ids():
    """
    Return pairs of Cree lemmas with their corresponding Wordform IDs.
    """
    return Wordform.objects.filter(is_lemma=True).values_list("text", "id")


class _Cache:
    """A holder for cached properties since caching module attributes is messy

    Could be made a singleton, but no need if only instantiated once in this
    file.
    """

    @cached_property
    def cree_affix_searcher(self) -> AffixSearcher:
        """
        Returns the affix searcher that matches Cree lemmas
        """
        return AffixSearcher(fetch_cree_lemmas_with_ids())

    @cached_property
    def english_affix_searcher(self) -> AffixSearcher:
        """
        Returns the affix searcher that matches English keywords (mined from the dictionary
        definitions
        """
        return AffixSearcher(fetch_english_keywords_with_ids())

    def preload(self):
        """Preload caches by accessing cached properties

        To be called on production server startup.
        """
        self.cree_affix_searcher
        self.english_affix_searcher


cache = _Cache()
