from collections import defaultdict
from itertools import chain
from typing import Dict, Iterable, List, Tuple

import dawg
from utils.cree_lev_dist import remove_cree_diacritics


class AffixSearcher:
    """
    Enables prefix and suffix searches given a list of words and their wordform IDs.
    """

    # TODO: "int" should be Wordform PK type
    # TODO: "str" should be InternalForm

    def __init__(self, words: List[Tuple[str, int]]):
        self.text_to_ids: Dict[str, List[int]] = defaultdict(list)

        for text, wordform_id in words:
            self.text_to_ids[self.to_simplified_form(text)].append(wordform_id)

        # TODO: why are there empty words in the first place?????
        non_empty_words = [t for t in words if len(t[0]) > 0]

        self._prefixes = dawg.CompletionDAWG([t[0] for t in non_empty_words])
        self._suffixes = dawg.CompletionDAWG([t[0][::-1] for t in non_empty_words])

    def search_by_prefix(self, prefix: str) -> Iterable[int]:
        """
        :return: an iterable of ids
        """
        # lower & remove diacritics
        prefix = self.to_simplified_form(prefix)
        return chain(*[self.text_to_ids[t] for t in self._prefixes.keys(prefix)])

    def search_by_suffix(self, suffix: str) -> Iterable[int]:
        """
        :return: an iterable of ids
        """
        # lower & remove diacritics
        suffix = self.to_simplified_form(suffix)

        return chain(
            *[self.text_to_ids[x[::-1]] for x in self._suffixes.keys(suffix[::-1])]
        )

    # TODO: return type should be InternalForm
    @staticmethod
    def to_simplified_form(query: str) -> str:
        """
        Convert to a simplified form of the word and its orthography to facilitate affix
        search.  You SHOULD throw out diacritics, choose a Unicode Normalization form,
        and choose a single letter case here!
        """
        # TODO: make this work for not just Cree!
        return remove_cree_diacritics(query.lower())
