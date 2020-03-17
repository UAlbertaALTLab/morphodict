#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Temporary HFSTOL.
"""

import shutil
from contextlib import contextmanager
from subprocess import DEVNULL, check_output
from tempfile import TemporaryFile
from typing import IO, Generator, Iterable, List, Tuple

from constants import Analysis
from utils.shared_res_dir import shared_res_dir as res

# Ensure we can load everything!
_analyzer_path = res / "fst" / "crk-descriptive-analyzer.hfstol"
assert _analyzer_path.exists()
_generator_path = res / "fst" / "crk-normative-generator.hfstol"
assert _generator_path.exists()

# Ensure HFST is callable.
_hfstol_bin = shutil.which("hfst-optimized-lookup")
if _hfstol_bin is None:
    raise ImportError("Cannot find hfst-optimized-lookup! Is it installed?")
else:
    _hfstol = _hfstol_bin


def analyze(wordform: str) -> Iterable[Analysis]:
    with write_temporary_file(f"{wordform}\n") as input_file:
        output = check_output(
            [_hfstol, "-q", _analyzer_path],
            stdin=input_file,
            stderr=DEVNULL,
            encoding="UTF-8",
        )

    raw_analyses = output.split("\n")
    return parse_analyses(raw_analyses)


def generate(analysis: str) -> Iterable[str]:
    with write_temporary_file(f"{analysis}\n") as input_file:
        output = check_output(
            [_hfstol, "-q", _generator_path],
            stdin=input_file,
            stderr=DEVNULL,
            encoding="UTF-8",
        )

    raw_transductions = output.split("\n")
    for line in raw_transductions:
        # Skip empty lines and failures to transduce.
        if line.strip() == "" or "+?" in line:
            continue

        _analysis, _tab, wordform = line.partition("\t")
        yield wordform


def parse_analyses(raw_analyses: Iterable[str]) -> Generator[Analysis, None, None]:
    """
    Given a list of lines from xfst/hfst output from the Plains Cree FST,
    yields analyses.

    This will break if using a different FST!
    """
    for line in raw_analyses:
        # hfst likes to output a bunch of empty lines. Ignore them.
        if line.strip() == "":
            continue

        input_form, _tab, analysis = line.rstrip().partition("\t")

        parts = analysis.split("+")
        prefixes, lemma_loc = find_prefixes(parts)
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


def find_prefixes(parts: List[str]) -> Tuple[List[str], int]:
    """
    Given a list of tags and stems from an analysis, returns the prefixes,
    and the presumed index of the lemma.

    >>> find_prefixes(["PV/e", "IC", "nipâw", "V", "AI", "Prs", "Cnj", "3Sg"])
    (['PV/e', 'IC'], 2)
    """
    prefixes = []
    for pos, prefix in enumerate(parts):
        # preverb or reduplication
        if prefix.startswith(("PV/", "Rd", "IC")):
            prefixes.append(prefix)
        else:
            # pos is now set to the position of the lemma.
            break
    return prefixes, pos


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
