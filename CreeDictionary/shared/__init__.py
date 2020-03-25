"""
shared (expensive) instances
"""

from hfstol import HFSTOL

from utils import paradigm_filler as pf
from utils import shared_res_dir

paradigm_filler = pf.ParadigmFiller.default_filler()

descriptive_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"
)

strict_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-strict-analyzer.hfstol"
)

normative_generator = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-normative-generator.hfstol"
)
