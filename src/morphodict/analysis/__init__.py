from functools import cache

from hfst_optimized_lookup import TransducerFile
from django.conf import settings

_fst_dir = settings.BASE_DIR / "resources" / "fst"


@cache
def strict_generator():
    return TransducerFile(_fst_dir / settings.STRICT_GENERATOR_FST_FILENAME)


@cache
def relaxed_analyzer():
    return TransducerFile(_fst_dir / settings.RELAXED_ANALYZER_FST_FILENAME)


@cache
def strict_analyzer():
    return TransducerFile(_fst_dir / settings.STRICT_ANALYZER_FST_FILENAME)
