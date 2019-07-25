"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
from os.path import dirname
from pathlib import Path
from typing import List, Dict, Tuple

from hfstol import HFSTOL

analyzer_file = Path(dirname(__file__)) / '..' / 'res' / 'fst' / 'crk-descriptive-analyzer.hfstol'

analyzer = HFSTOL.from_file(analyzer_file)


def expand(xml_lemma_to_pos_lc: Dict[str, Tuple[str, str]]) -> Dict[str, List[str]]:
    """
    for every inflection in inflections, generate its sibling inflections

    <pos> and <lc> from xml file  are used to determine the paradigm to use for every lemma
    """
    inflections = xml_lemma_to_pos_lc.keys()

    xml_lemma_to_analyses = analyzer.feed_in_bulk_fast(inflections)



