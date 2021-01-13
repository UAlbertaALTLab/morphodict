from collections import defaultdict
from itertools import chain
from typing import Dict, Iterable, List, Tuple

import dawg
from utils.cree_lev_dist import remove_cree_diacritics


class AffixSearcher:

    # TODO: "int" should be Wordform PK type
    # TODO: "str" should be InternalForm

    def __init__(self, words: List[Tuple[str, int]]):
        """
        :param words: expects lowered, no diacritics words with their ids
        """
        self.text_to_ids: Dict[str, List[int]] = defaultdict(list)
        for w, w_id in words:
            self.text_to_ids[w].append(w_id)

        # TODO: why are there empty words in the first place?????
        non_empty_words = [t for t in words if len(t[0]) > 0]

        self.trie = dawg.CompletionDAWG([t[0] for t in non_empty_words])
        self.inverse_trie = dawg.CompletionDAWG([t[0][::-1] for t in non_empty_words])

    def search_by_prefix(self, prefix: str) -> Iterable[int]:
        """
        :return: an iterable of ids
        """
        # lower & remove diacritics
        prefix = self.to_internal_form(prefix)
        return chain(*[self.text_to_ids[t] for t in self.trie.keys(prefix)])

    def search_by_suffix(self, suffix: str) -> Iterable[int]:
        """
        :return: an iterable of ids
        """
        # lower & remove diacritics
        suffix = self.to_internal_form(suffix)

        return chain(
            *[self.text_to_ids[x[::-1]] for x in self.inverse_trie.keys(suffix[::-1])]
        )

    # TODO: return type should be InternalForm
    @staticmethod
    def to_internal_form(query: str) -> str:
        # TODO: make this work for not just Cree!
        return remove_cree_diacritics(query.lower())
