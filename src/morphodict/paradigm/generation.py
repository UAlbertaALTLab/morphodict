"""
Handles paradigm generation.
"""

from django.conf import settings


import morphodict.analysis
from morphodict.paradigm.manager import (
    ParadigmManager,
    ParadigmManagerWithExplicitSizes,
)
from morphodict.site.util import cache_unless


@cache_unless(settings.DEBUG_PARADIGM_TABLES)
def default_paradigm_manager() -> ParadigmManager:
    """
    Returns the ParadigmManager instance that loads layouts and FST from the res
    (resource) directory for the crk/eng language pair (itwêwina).

    Affected by:
      - MORPHODICT_PARADIGM_SIZE_ORDER
    """

    layout_dir = settings.BASE_DIR / ".." / "morphodict" / "paradigm" / "layouts"

    site_specific_layout_dir = settings.BASE_DIR / "resources" / "layouts"
    if site_specific_layout_dir.exists():
        layout_dir = site_specific_layout_dir

    generator = morphodict.analysis.strict_generator()

    if hasattr(settings, "MORPHODICT_PARADIGM_SIZES"):
        return ParadigmManagerWithExplicitSizes(
            layout_dir,
            generator,
            ordered_sizes=settings.MORPHODICT_PARADIGM_SIZES,
        )
    else:
        return ParadigmManager(layout_dir, generator)
