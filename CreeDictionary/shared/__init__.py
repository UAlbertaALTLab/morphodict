"""
shared (expensive) instances
"""

from hfstol import HFSTOL

from utils import shared_res_dir

descriptive_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"
)

strict_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-strict-analyzer.hfstol"
)

generator = HFSTOL.from_file(shared_res_dir / "fst" / "crk-normative-generator.hfstol")
