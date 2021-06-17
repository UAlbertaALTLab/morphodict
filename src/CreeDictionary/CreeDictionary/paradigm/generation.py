"""
Handles paradigm generation.
"""

from functools import cache

import morphodict.analysis
from CreeDictionary.CreeDictionary.paradigm.manager import ParadigmManager
from CreeDictionary.utils import shared_res_dir


@cache
def default_paradigm_manager() -> ParadigmManager:
    """
    Returns the ParadigmManager instance that loads layouts and FST from the res
    (resource) directory for the crk/eng language pair (itwêwina).
    """
    return ParadigmManager(
        shared_res_dir / "layouts", morphodict.analysis.strict_generator()
    )
