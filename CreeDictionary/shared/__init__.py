"""
shared (expensive) instances
"""

from typing import Dict, Iterable, Set, Tuple

from utils import shared_res_dir

from .expensive import descriptive_analyzer, normative_generator, paradigm_filler
from .workaround import HFSTOLWithoutFragmentAnalyses

_fst_dir = shared_res_dir / "fst"


strict_analyzer = HFSTOLWithoutFragmentAnalyses.from_file(
    _fst_dir / "crk-strict-analyzer.hfstol"
)
