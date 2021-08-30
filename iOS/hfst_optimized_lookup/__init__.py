from pathlib import Path

from ._types import Analysis
from _hfst_optimized_lookup import TransducerFile

__all__ = ["TransducerFile", "Analysis"]

#__version__ = (Path(__file__).parent / "VERSION").read_text().strip()
