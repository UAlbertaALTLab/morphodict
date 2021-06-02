from functools import cache

from hfst_optimized_lookup import TransducerFile
from CreeDictionary.utils import shared_res_dir

_fst_dir = shared_res_dir / "fst"


@cache
def strict_generator():
    return TransducerFile(_fst_dir / "crk-strict-generator.hfstol")


@cache
def relaxed_analyzer():
    return TransducerFile(_fst_dir / "crk-relaxed-analyzer-for-dictionary.hfstol")


@cache
def strict_analyzer():
    return TransducerFile(_fst_dir / "crk-strict-analyzer-for-dictionary.hfstol")
