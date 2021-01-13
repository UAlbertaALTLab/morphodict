#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from hfstol import HFSTOL
from utils import paradigm_filler as pf
from utils import shared_res_dir

_fst_dir = shared_res_dir / "fst"

paradigm_filler = pf.ParadigmFiller.default_filler()

normative_generator = HFSTOL.from_file(_fst_dir / "crk-normative-generator.hfstol")
