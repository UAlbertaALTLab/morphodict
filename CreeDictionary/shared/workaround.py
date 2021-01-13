#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Workaround for FSTs that return both a normal analysis AND an +Err/Frag analysis.

We don't want the +Err/Frag analyses!
"""

from typing import Dict, Iterable, Set, Tuple

from hfstol import HFSTOL


class HFSTOLWithoutFragmentAnalyses:
    """
    Acts like HFSTOL but removes analyses with +Err/Frag.
    """

    def __init__(self, transducer: HFSTOL):
        self._hfstol = transducer

    @staticmethod
    def _is_good_analysis(analysis: str) -> bool:
        return "+Err/Frag" not in analysis

    def feed_in_bulk_fast(
        self, surface_forms: Iterable[str], multi_process: int = 1
    ) -> Dict[str, Set[str]]:
        original = self._hfstol.feed_in_bulk_fast(
            surface_forms, multi_process=multi_process
        )
        return {
            wordform: {a for a in analyses if self._is_good_analysis(a)}
            for wordform, analyses in original.items()
        }

    @classmethod
    def from_file(cls, path) -> HFSTOL:
        return cls(HFSTOL.from_file(path))
