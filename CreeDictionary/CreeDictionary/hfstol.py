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

    raw_prefixes: str
    lemma: str
    raw_suffixes: str


def analyze(wordform: str) -> Generator[Analysis, None, None]:
    with write_temporary_file(f"{wordform}\n") as input_file:
        output = check_output(
            [_hfstol, "-q", _analyzer_path],
            stdin=input_file,
            stderr=DEVNULL,
            encoding="UTF-8",
        )

    raw_analyses = output.split("\n")

    for line in raw_analyses:
        # hfst likes to output a bunch of empty lines. Ignore them.
        if line.strip() == "":
            continue

        input_form, _tab, analysis = line.rstrip().partition("\t")

        parts = analysis.split("+")
        prefixes = []
        for lemma_loc, prefix in enumerate(parts):
            if prefix.startswith("PV/") or prefix.startswith("Rd"):
                prefixes.append(prefix)
            else:
                break
        lemma = parts[lemma_loc]
        suffixes = parts[lemma_loc + 1 :]

        # Faild to analyze term
        if suffixes == ["?"]:
            continue

        yield Analysis(
            raw_prefixes="+".join(prefixes),
            lemma=lemma,
            raw_suffixes="+".join(suffixes),
        )


@contextmanager
def write_temporary_file(text: str) -> Generator[IO[str], None, None]:
    """
    Creates a temporary file and writes all of its text as UTF-8.

    This is useful as the stdin to subprocess.check_output().
    """
    with TemporaryFile("w+", encoding="UTF-8") as tmp:
        tmp.write(text)
        tmp.flush()
        tmp.seek(0)
        yield tmp
