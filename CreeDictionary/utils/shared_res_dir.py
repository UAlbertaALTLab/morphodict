"""
Gives the path to the shared resources ("res") folder.
"""
from pathlib import Path

shared_res_dir: Path = Path(__file__).parent.parent / "res"
