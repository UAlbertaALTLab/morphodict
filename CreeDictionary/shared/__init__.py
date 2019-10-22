"""
shared (expensive) instances
"""

from hfstol import HFSTOL
from fst_lookup import FST

from utils import shared_res_dir


descriptive_analyzer_foma = FST.from_file(
    shared_res_dir / "fst/crk-descriptive-analyzer.fomabin"
)

descriptive_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"
)

strict_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-strict-analyzer.hfstol"
)

normative_generator = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-normative-generator.hfstol"
)
