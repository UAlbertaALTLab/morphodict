from collections import defaultdict
from itertools import chain

import marisa_trie
from typing import List, Iterable, Tuple, Dict


class AffixSearcher:
    def __init__(self, words: Iterable[Tuple[str, int]]):
        """
        :param words: expects lowered, no diacritics words with their ids
        """
        self.text_to_ids: Dict[str, List[int]] = defaultdict(list)
        for w, w_id in words:
            self.text_to_ids[w].append(w_id)

        self.trie = marisa_trie.Trie([t[0] for t in words])
        self.inverse_trie = marisa_trie.Trie([t[0][::-1] for t in words])

    def search_by_prefix(self, prefix: str) -> Iterable[int]:
        """
        :param prefix: expects lowered, no diacritics words
        :return: an iterable of ids
        """
        return chain(*[self.text_to_ids[t] for t in self.trie.keys(prefix)])

    def search_by_suffix(self, suffix: str) -> Iterable[int]:
        """
        :param suffix: expects lowered, no diacritics words
        :return: an iterable of ids
        """
        return chain(
            *[self.text_to_ids[x[::-1]] for x in self.inverse_trie.keys(suffix[::-1])]
        )
