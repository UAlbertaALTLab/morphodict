#!/usr/bin/env python3

"""
Updates layout files. Can download them from the old itwêwina -- not
recommended.
"""

import argparse
import subprocess
import sys
from contextlib import contextmanager
from glob import glob
from os import chdir, getcwd
from pathlib import Path
from tempfile import TemporaryDirectory

from utils import shared_res_dir
from utils.paradigm_layout_combiner import combine_layout_paradigm


def update():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--download-from-old-itwewina", default=False, action="store_true"
    )
    args = parser.parse_args()

    if args.download_from_old_itwewina:
        download_from_old_itwewina()

    combine_layout_paradigm()


def download_from_old_itwewina():
    """
    1. Pull layout AND paradigm files from itwewina and place them correctly
    2. combine them to res/prefilled-layouts/
    https://github.com/UAlbertaALTLab/itwewina/tree/development/neahtta/configs/language_specific_rules/paradigms/crk
    """
    with TemporaryDirectory() as temp_dir, cd(temp_dir):
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


@contextmanager
def cd(path):
    curdir = getcwd()
    try:
        chdir(curdir)
        yield
    finally:
        chdir(curdir)
