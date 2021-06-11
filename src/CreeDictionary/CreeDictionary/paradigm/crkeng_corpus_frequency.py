import logging

from CreeDictionary.utils import shared_res_dir
from CreeDictionary.utils.types import ConcatAnalysis

CORPUS_FREQUENCY_FILE = shared_res_dir / "corpus_frequency.txt"

logger = logging.getLogger(__name__)


def import_frequency() -> dict[ConcatAnalysis, int]:
    """
    Corpus frequency is stored in a bespoke file format. This parses that file and
    returns a dictionary.
    """
    # TODO: store this in the database, rather than as a source file
    # TODO: make a management command that updates wordform frequencies

    res: dict[ConcatAnalysis, int] = {}
    lines = CORPUS_FREQUENCY_FILE.read_text(encoding="UTF-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            # Skip empty lines
            continue

        try:
            freq, _, *analyses = line.split()
        except ValueError:
            # not enough value to unpack, which means the line has less than 3 values
            logger.warning(f'line "{line}" is broken in {CORPUS_FREQUENCY_FILE}')
        else:
            for analysis in analyses:
                res[ConcatAnalysis(analysis)] = int(freq)

    return res
