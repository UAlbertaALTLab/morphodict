#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Workaround for FSTs that return both a normal analysis AND an +Err/Frag analysis.

We don't want the +Err/Frag analyses!
"""

# For “classmethod returning instance” in .from_file() type
# https://stackoverflow.com/a/53450349/14558
from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from hfst_optimized_lookup import TransducerFile


class HFSTOLWithoutFragmentAnalyses:
    """
    Acts like HFSTOL but removes analyses with +Err/Frag.
    """

    def __init__(self, transducer: TransducerFile):
        self._hfstol = transducer

    @staticmethod
    def _is_good_analysis(analysis: str) -> bool:
        return "+Err/Frag" not in analysis

    def lookup(self, word) -> List[str]:
        return self._hfstol.lookup(word)

    def bulk_lookup(self, surface_forms: Iterable[str]) -> Dict[str, Set[str]]:
        original = self._hfstol.bulk_lookup(surface_forms)
        return {
            wordform: {a for a in analyses if self._is_good_analysis(a)}
            for wordform, analyses in original.items()
        }

    @classmethod
    def from_file(cls, path) -> HFSTOLWithoutFragmentAnalyses:
        return cls(TransducerFile(path))
