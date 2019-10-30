#!/usr/bin/env python
import subprocess
import sys
from glob import glob
from os import chdir
from pathlib import Path
from tempfile import TemporaryDirectory

from utils import shared_res_dir
from utils.paradigm_layout_combiner import combine_layout_paradigm


def update():
    """
    1. Pull layout AND paradigm files from itwewina and place them correctly
    2. combine them to res/prefilled-layouts/
    https://github.com/UAlbertaALTLab/itwewina/tree/development/neahtta/configs/language_specific_rules/paradigms/crk
    """
    with TemporaryDirectory() as temp_dir:
        chdir(temp_dir)
        subprocess.run(
            [
                "gitdir",
                "--flatten",
                "https://github.com/UAlbertaALTLab/itwewina/tree/development/neahtta/configs/language_specific_rules/paradigms/crk",
            ],
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        layouts = glob("*.layout")
        paradigms = glob("*.paradigm")

        for file in (shared_res_dir / "layouts").iterdir():
            file.unlink()
        for file in (shared_res_dir / "paradigms").iterdir():
            file.unlink()

        for layout in layouts:
            Path(layout).rename(shared_res_dir / "layouts" / Path(layout).name)
        for paradigm in paradigms:
            Path(paradigm).rename(
                str(shared_res_dir / "paradigms" / Path(paradigm).name)
            )
        combine_layout_paradigm()
