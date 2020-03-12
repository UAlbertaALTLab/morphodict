#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Temporary HFSTOL.
"""

import shutil
from contextlib import contextmanager
from subprocess import DEVNULL, check_output
from tempfile import TemporaryFile
from typing import IO, Generator, Iterable, NamedTuple

from utils.shared_res_dir import shared_res_dir as res

# Ensure we can load everything!
_analyzer_path = res / "fst" / "crk-descriptive-analyzer.hfstol"
assert _analyzer_path.exists()
_hfstol_bin = shutil.which("hfst-optimized-lookup")
if _hfstol_bin is None:
    raise ImportError("Cannot find hfst-optimized-lookup! Is it installed?")
else:
    _hfstol = _hfstol_bin


class Analysis(NamedTuple):
    """
    Analysis of a wordform.
    """

    lemma: str
    raw_suffixes: str


@contextmanager
def write_file(text: str) -> Generator[IO[str], None, None]:
    with TemporaryFile("w+", encoding="UTF-8") as tmp:
        tmp.write(text)
        tmp.flush()
        tmp.seek(0)
        yield tmp


def analyze(wordform: str) -> Generator[Analysis, None, None]:
    with write_file(f"{wordform}\n") as input_file:
        output = check_output(
            [_hfstol, "-q", _analyzer_path],
            stdin=input_file,
            stderr=DEVNULL,
            encoding="UTF-8",
        )

    *raw_analyses, blank_line = output.split("\n")
    assert blank_line.strip() == ""

    for line in raw_analyses:
        input_form, _tab, analysis = line.partition("\t")
        lemma, _plus, suffixes = analysis.partition("+")
        yield Analysis(lemma=lemma, raw_suffixes=suffixes)
