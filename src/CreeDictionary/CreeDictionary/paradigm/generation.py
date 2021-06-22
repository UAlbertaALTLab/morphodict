"""
Handles paradigm generation.
"""

from functools import cache

from django.conf import settings

import morphodict.analysis
from CreeDictionary.CreeDictionary.paradigm.manager import (
    ParadigmManager,
    ParadigmManagerWithExplicitSizes,
)
from CreeDictionary.utils import shared_res_dir


@cache
def default_paradigm_manager() -> ParadigmManager:
    """
    Returns the ParadigmManager instance that loads layouts and FST from the res
    (resource) directory for the crk/eng language pair (itwêwina).

    Affected by:
      - MORPHODICT_PARADIGM_SIZE_ORDER
    """

    layout_dir = shared_res_dir / "layouts"
    generator = morphodict.analysis.strict_generator()

    if hasattr(settings, "MORPHODICT_PARADIGM_SIZES"):
        return ParadigmManagerWithExplicitSizes(
            layout_dir,
            generator,
            ordered_sizes=settings.MORPHODICT_PARADIGM_SIZES,
        )
    else:
        return ParadigmManager(layout_dir, generator)
