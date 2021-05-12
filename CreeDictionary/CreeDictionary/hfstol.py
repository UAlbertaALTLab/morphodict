#!/usr/bin/env python3

"""
Run finite-state transducer analyzer and generator
"""

from typing import Generator, Iterable, List, Tuple

from CreeDictionary.shared.expensive import relaxed_analyzer, strict_generator
from CreeDictionary.utils.data_classes import Analysis


def analyze(wordform: str) -> Iterable[Analysis]:
    return parse_analyses(relaxed_analyzer.lookup(wordform))


def generate(analysis: str) -> Iterable[str]:
    return strict_generator.lookup(analysis)


def parse_analyses(raw_analyses: Iterable[str]) -> Generator[Analysis, None, None]:
    """
    Given a list of lines from xfst/hfst output from the Plains Cree FST,
    yields analyses.

    This will break if using a different FST!
    """
    for analysis in raw_analyses:
        parts = analysis.split("+")
        prefixes, lemma_loc = find_prefixes(parts)
        lemma = parts[lemma_loc]
        suffixes = parts[lemma_loc + 1 :]

        # Failed to analyze term
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
