#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from hfst_optimized_lookup import TransducerFile
from utils import paradigm_filler as pf
from utils import shared_res_dir

from .workaround import HFSTOLWithoutFragmentAnalyses

_fst_dir = shared_res_dir / "fst"

# These are part of the public API, but don't instantiate them yet!
paradigm_filler: pf.ParadigmFiller
strict_generator: TransducerFile
relaxed_analyzer: TransducerFile
strict_analyzer: TransducerFile

# How to create one of the above 👆🏼 instances
_instance_factory = dict(
    paradigm_filler=lambda: pf.ParadigmFiller.default_filler(),
    strict_generator=lambda: TransducerFile(
        _fst_dir / "crk-strict-generator.hfstol"
    ),
    relaxed_analyzer=lambda: HFSTOLWithoutFragmentAnalyses.from_file(
        _fst_dir / "crk-relaxed-analyzer-for-dictionary.hfstol"
    ),
    strict_analyzer=lambda: HFSTOLWithoutFragmentAnalyses.from_file(
        _fst_dir / "crk-strict-analyzer-for-dictionary.hfstol"
    ),
)


def __getattr__(name: str):
    """
    Implements lazy/deferred instantiation for the expensive instances above.

    When an instance is accessed for the very first time, e.g.,

        from shared import expensive
        expensive.relaxed_analyzer

    That instance will NOT exist in the module namespace (i.e., globals()).
    Since Python 3.7, we can intercept this access, and PERMANENTLY add that instance to
    the module.

    See: https://www.python.org/dev/peps/pep-0562/
    """

    if name not in _instance_factory:
        # not something we can instantiate:
        raise AttributeError(name)

    return _create_instance_and_add_to_module_permanently(name)


def _create_instance_and_add_to_module_permanently(name):
    return globals().setdefault(name, _instance_factory[name]())
