#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from hfstol import HFSTOL
from utils import paradigm_filler as pf
from utils import shared_res_dir

from .workaround import HFSTOLWithoutFragmentAnalyses

_fst_dir = shared_res_dir / "fst"

# These are part of the public API, but don't instantiate them yet!
paradigm_filler: pf.ParadigmFiller
normative_generator: HFSTOL
descriptive_analyzer: HFSTOL
strict_analyzer: HFSTOL

# How to create one of the above 👆🏼 instances
_instance_factory = dict(
    paradigm_filler=lambda: pf.ParadigmFiller.default_filler(),
    normative_generator=lambda: HFSTOL.from_file(
        _fst_dir / "crk-normative-generator.hfstol"
    ),
    descriptive_analyzer=lambda: HFSTOLWithoutFragmentAnalyses.from_file(
        _fst_dir / "crk-descriptive-analyzer.hfstol"
    ),
    strict_analyzer=lambda: HFSTOLWithoutFragmentAnalyses.from_file(
        _fst_dir / "crk-strict-analyzer.hfstol"
    ),
)


def __getattr__(name: str):
    """
    Implements lazy/deferred instantiation for the expensive instances above.

    When an instance is accessed for the very first time, e.g.,

        from shared import expensive
        expensive.descriptive_analyzer

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
