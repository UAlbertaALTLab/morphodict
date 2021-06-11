import logging
from functools import cache

from CreeDictionary.utils import shared_res_dir
from CreeDictionary.utils.types import ConcatAnalysis

CORPUS_FREQUENCY_FILE = shared_res_dir / "corpus_frequency.txt"

logger = logging.getLogger(__name__)


def import_frequency() -> dict[ConcatAnalysis, int]:
    """
    Corpus frequency is stored in a bespoke file format. This parses that file and
    returns a dictionary mapping the ANALYSIS to the amount of times it has appeard
    in the corpus.
    """
    return {analysis: frequency for _, analysis, frequency in import_tuples()}


def import_tuples() -> list[tuple[str, ConcatAnalysis, int]]:
    # TODO: store this in the database, rather than as a source file
    # TODO: make a management command that updates wordform frequencies

    result = []
    lines = CORPUS_FREQUENCY_FILE.read_text(encoding="UTF-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            # Skip empty lines
            continue

        try:
            freq, wordform, *analyses = line.split()
        except ValueError:
            # not enough value to unpack, which means the line has less than 3 values
            logger.warning(f'line "{line}" is broken in {CORPUS_FREQUENCY_FILE}')
            continue

        for analysis in analyses:
            result.append((wordform, ConcatAnalysis(analysis), int(freq)))

    return result


@cache
def observed_wordforms() -> set[str]:
    """
    Return a set of wordforms that have been observed in some corpus.

    As of 2021-06-11, for itwêwina, this information is derived from the
    corpus_frequency.txt file that is checked-in to the repo.
    """
    return {wordform for wordform, _analysis, freq in import_tuples() if freq > 0}
